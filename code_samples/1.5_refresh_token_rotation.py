# Excerpt of app/services/account_service.py lines 481-656 (Mukham). Not runnable alone.
# Git blame: 161 lines Arin, 15 lines a teammate.

def start_session(
    db: Session,
    user: User,
    device_name: str | None = None,
) -> str:
    """
    Start a token family for a newly signed-in device and return its first
    refresh token. The caller commits.
    """
    now = datetime.now(timezone.utc)
    family_id = secrets.token_hex(16)

    db.add(
        RefreshTokenFamily(
            family_id=family_id,
            mobile_number=user.mobile_number,
            device_name=(device_name or "").strip()[:100] or None,
            created_at=now,
            last_used_at=now,
        )
    )

    return create_refresh_token(user.mobile_number, family_id)


def _record_used_token(db: Session, payload: dict, now: datetime) -> None:
    db.add(
        RevokedRefreshToken(
            jti=str(payload["jti"]),
            mobile_number=str(payload["mobile_number"]),
            expires_at=datetime.fromtimestamp(int(payload["exp"]), tz=timezone.utc),
            revoked_at=now,
        )
    )


def _revoke_family(
    db: Session,
    family_id: str,
    reason: str,
    now: datetime,
) -> None:
    family = db.get(RefreshTokenFamily, family_id)
    if family is not None and family.revoked_at is None:
        family.revoked_at = now
        family.revoked_reason = reason


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    payload = decode_refresh_token(refresh_token)

    if payload is None:
        raise AccountError(401, INVALID_REFRESH_TOKEN)

    user = (
        db.query(User)
        .filter(User.mobile_number == str(payload["mobile_number"]))
        .first()
    )

    if user is None or not user.is_active:
        raise AccountError(401, INVALID_REFRESH_TOKEN)

    family_id = payload.get("fam")
    now = datetime.now(timezone.utc)

    already_used = (
        db.query(RevokedRefreshToken)
        .filter(RevokedRefreshToken.jti == str(payload["jti"]))
        .first()
    )

    if already_used is not None:
        # Each refresh token works once. Seeing one again means a copy is
        # in someone else's hands, so sign that device out entirely.
        if family_id:
            _revoke_family(db, family_id, "token_reuse", now)
            db.commit()
            logger.warning(
                "Refresh token reused; revoked token family %s for %s",
                family_id,
                user.mobile_number,
            )
        raise AccountError(401, INVALID_REFRESH_TOKEN)

    family = None
    if family_id:
        family = (
            db.query(RefreshTokenFamily)
            .filter(RefreshTokenFamily.family_id == family_id)
            .with_for_update()
            .first()
        )
        if (
            family is None
            or family.revoked_at is not None
            or family.mobile_number != user.mobile_number
        ):
            db.rollback()
            raise AccountError(401, INVALID_REFRESH_TOKEN)

    try:
        # The primary key on jti stops the same refresh token from being
        # rotated twice, including by concurrent requests.
        _record_used_token(db, payload, now)

        if family is None:
            # Issued before token families existed: give it a family now.
            new_refresh = start_session(db, user)
        else:
            family.last_used_at = now
            new_refresh = create_refresh_token(user.mobile_number, family.family_id)

        role = "organization" if user.is_organization else "employee"
        claims = {"role": role}

        if user.is_organization:
            claims["org_id"] = user.org_id

        new_access = create_access_token(
            user.mobile_number,
            claims,
        )

        db.commit()

    except IntegrityError:
        db.rollback()
        raise AccountError(401, INVALID_REFRESH_TOKEN)

    except Exception:
        db.rollback()
        raise

    return {
        "access": new_access,
        "refresh": new_refresh,
        "token_type": "bearer",
    }


def end_session(db: Session, refresh_token: str) -> None:
    """
    Sign a device out: revoke its token family, so none of its refresh
    tokens work again. Invalid or expired tokens are ignored, so signing
    out always succeeds. Access tokens already issued stay valid until
    they expire (at most 60 minutes).
    """
    payload = decode_refresh_token(refresh_token)

    if payload is None:
        return

    now = datetime.now(timezone.utc)

    try:
        if payload.get("fam"):
            _revoke_family(db, str(payload["fam"]), "sign_out", now)

        already_used = (
            db.query(RevokedRefreshToken)
            .filter(RevokedRefreshToken.jti == str(payload["jti"]))
            .first()
        )
        if already_used is None:
            _record_used_token(db, payload, now)

        db.commit()

    except IntegrityError:
        # Revoked by a concurrent request; the outcome is the same.
        db.rollback()

    except Exception:
        db.rollback()
        raise
