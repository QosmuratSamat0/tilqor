# 0003. The user role is the single source of Tilqor permissions

- **Status:** Accepted
- **Date:** 2026-10-31
- **Source:** FR-02; TIL-20 (PR #17); TIL-21 commit `fc47d32` (createsuperuser gets the admin role)

## Context
Django already has `is_staff`, `is_superuser` and model permissions. Tilqor needs four product roles
(participant, reviewer, moderator, administrator) checked on the server for every action (FR-02).
Two parallel permission systems would disagree.

## Decision
- `User.role` decides what a user may do in Tilqor: `is_reviewer`, `is_moderator`, `is_admin_role`.
- API permissions are classes in `common/permissions.py` (`IsReviewer`, `IsModerator`).
- Django admin views also check the role (for example, only moderators manage tasks).
- `is_superuser` only affects Django admin model permissions; `createsuperuser` sets `role = admin`.

## Consequences
- One place to check and test permissions per role.
- Giving someone reviewer access means changing the role, not Django groups.
