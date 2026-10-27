# Focus areas

Load from step 2 of the review. The first column is the `layer` argument value; the second is the
finding's Category.

| Focus | Category | Look for |
|---|---|---|
| types | TYPE_MISMATCH | Frontend types that disagree with backend responses in field names, types, or nullability. Assertions (`as`, `!`) that hide a reachable contract mismatch; prove it at the boundary. Inconsistency along the database column, backend type, frontend type chain. Nullability mismatches between layers, defensive null checks that signal an unclear contract, inconsistent default values. |
| transforms | TRANSFORMATION | Redundant transformations (snake_case to camelCase in several places). Transformations the API layer could do. Client-side renaming, reshaping, or calculation the API could provide. |
| contract | API_DESIGN | Over-fetching (unused fields). Under-fetching (several calls to assemble one response). N+1 patterns and calls that could be consolidated or split. Inconsistent response shapes across similar endpoints. Computed fields the server could provide. |
| errors | ERROR_HANDLING | Inconsistent error shapes between API and client. Client guessing at error structure without typed errors. Silent failures or swallowed errors at the integration boundary. |
| validation | VALIDATION | Missing authoritative server-side validation at a trust boundary. Client and server rules that contradict one another on reachable inputs. Business rules in both layers that could drift apart. |
| naming | CONVENTION | Inconsistent naming across the stack. Different names for the same concept. Magic strings that should be shared constants. |
