# 📚 Release History (Pre–0.5.6)

⚠️ Starting from version **0.5.6**, versioning and changelog are managed automatically via GitHub Releases.  
For earlier versions (before 0.5.6), automation was not yet in place.  
The following table provides a summary of all pre–0.5.6 releases.

---

## 📜 Versions Overview

| Version | Date       | Description | Release Type   | Target Branch | Version Type | PR Author |
|---------|------------|-------------|----------------|---------------|--------------|-----------|
| 0.1.0   | 2025-06-03 | Project initialization <br> • Set up hexagonal architecture <br> • Created SQL adapter (SQLAlchemy) and database tables <br> • Structured packages: domain, port, service, entrypoint (FastAPI API) | Pre-production | develop | New features | @Baptiste-Ferrand |
| 0.1.1   | 2025-06-05 | Fix – Dependencies & sessions <br> • Fixed DB session passing from API entrypoints to services <br> • Added container to organize repositories and sessions, avoiding cross-layer dependencies | Pre-production | develop | Bug fixes | @Baptiste-Ferrand |
| 0.2.0   | 2025-06-10 | Profiles, groups & authentication management <br> • CRUD for profiles <br> • CRUD for groups <br> • Implemented JWT token <br> • Role & permission management (isAdmin, isOwner, etc.) | Pre-production | develop | New features | @Baptiste-Ferrand |
| 0.2.1   | 2025-06-11 | Fix – Permissions <br> • Fixed bug where *isOwner* permissions were not correctly checked when adding a member to a group | Pre-production | develop | Bug fixes | @Baptiste-Ferrand |
| 0.3.0   | 2025-06-14 | Trainings, exercises & tasks management <br> • Full CRUD for exercises <br> • CRUD for trainings <br> • CRUD for tasks <br> • CRUD for task validation | Pre-production | develop | New features | @Baptiste-Ferrand |
| 0.3.1   | 2025-06-16 | Fix – Regression on exercises <br> • Fixed regression: deleting a training did not delete its associated tasks | Pre-production | develop | Bug fixes | @Baptiste-Ferrand |
| 0.4.0   | 2025-06-20 | Diets & meal plans management <br> • CRUD for diets <br> • CRUD for meal plans <br> • CRUD for macro plans | Pre-production | develop | New features | @Baptiste-Ferrand |
| 0.5.0   | 2025-06-28 | InMemory adapter & integration tests <br> • Added InMemory adapter for local storage and testing <br> • Added integration tests covering all endpoints | Pre-production | develop | New features | @Baptiste-Ferrand |
| 0.5.1   | 2025-06-29 | Fix – Integration tests <br> • Refactored poorly designed tests (groups, profiles) <br> • Fixed InMemory fixtures configuration | Pre-production | develop | Bug fixes | @Baptiste-Ferrand |
| 0.5.2   | 2025-06-30 | Fix – Diet/macro plan/meal plan <br> • Fixed total calories format (returned as string instead of float) <br> • Fixed API response display bug for total calories | Pre-production | develop | Bug fixes | @Baptiste-Ferrand |
| 0.5.3   | 2025-07-01 | Fix – Training/tasks/validation <br> • Fixed bug preventing deletion of tasks linked to deleted trainings <br> • Added tests to guarantee cascade deletion | Pre-production | develop | Bug fixes | @Baptiste-Ferrand |
| 0.5.4   | 2025-07-02 | Fix – Side effect <br> • Fixed bug where deleting a meal plan sometimes wrongly deleted related diets | Pre-production | develop | Bug fixes | @Baptiste-Ferrand |
| 0.5.5   | 2025-07-03 | Refactor – Convention & readability <br> • Refactored function names to follow PEP8 <br> • Cleaned imports and typing | Pre-production | develop | Bug fixes | @Baptiste-Ferrand |
