# Coverage Assignment Reference

This document summarizes the behavior implemented in [`coverage_assignments.py`](coverage_assignments.py). It describes the code's current output, not a coaching recommendation or a universal rule for these coverages.

## How to Read This Guide

`assign()` returns `(primary_position, double_team_position)`. These are defensive position labels, not player names. The game service later finds a defender in that position; if the defense has no player at the assigned position, the player lookup can still fail.

The defensive formation string usually contains a front, personnel group, and coverage, for example `43 Under, Nickel Personnel, Cover-4`. The assignment classes inspect these substrings:

| ---------------- | ------------------------------- |
| Formation detail | Meaning to the assignment logic |
| `43`             | 4-3 front check                 |
| `34`             | 3-4 front check                 |
| `Regular`        | Regular personnel check         |
| `Nickel`         | Nickel personnel check          |
| `Dime`           | Dime personnel check            |

The checks are substring tests. Most methods do not validate that the formation has exactly one front or personnel group; unmatched combinations can leave an assignment as `None`.

### Offensive Position Aliases

The game service maps eligible receivers into the positions used by the assignment classes:

| ----------------- | ------------------- |
| Game-log position | Assignment position |
| `SLOT` (first)    | `R`                 |
| `SLOT` (second)   | `S`                 |
| `SLOT` (third)    | `V`                 |
| `TE` (first)      | `Y`                 |
| `TE` (second)     | `T`                 |
| `TE` (third)      | `U`                 |

`X(SE)`, `Z(FL)`, `RB`, and `FB` are used directly. Several branches also depend on offensive formation tokens such as `014`, `014t`, `023`, `131`, `Weak`, and `Pro`.

### Route Names

The implementation matches these exact route labels:

| ----------------------- | ------------------------------------------------------------------------------------------------- |
| Route group             | Exact route labels                                                                                |
| Flat / short outside    | `S Screen (S)`, `F Flat (0-4)`, `1 Out (5-8)`, `3 Comeback (9-12)`                                |
| Short inside            | `0 Dig (0-4)`, `2 Slant (5-8)`, `4 Curl (9-12)`                                                   |
| Deep inside             | `6 Deep In (13-18)`, `8 Post (19-26)`                                                             |
| Deep outside / vertical | `5 Deep Out (13-18)`, `7 Corner (19-26)`, `9 Fade (27-39)`, `D Deep Fade (40+)`, `W Wheel (9-18)` |

## Man Coverage

Route does not affect the primary assignment. It only matters indirectly if the caller interprets the assignment as man coverage.

| -------------------------------- | ------------------------------------------------------------------------ | ---------------- | --------------- |
| Defensive formation condition    | Offensive player / formation                                             | Primary defender | Double defender |
| Any                              | `X(SE)`; `Z(FL)` in `131`; `T` in `221` or `230`                         | LCB              | None            |
| Any                              | Other `Z(FL)` or `U`                                                     | RCB              | None            |
| Any                              | `R` in `014`, `023`, or `113`                                            | NB               | None            |
| Any                              | `V`                                                                      | SS               | None            |
| Any                              | `R` in `005`, `014t`, `113t`, or `203`                                   | NB               | None            |
| Any                              | `S`                                                                      | DB               | None            |
| Any                              | `Y` in `014t`                                                            | SS               | None            |
| Regular                          | `T` in `023`, `122`, or `131`                                            | WLB              | None            |
| Nickel or Dime                   | `T` in `023`                                                             | WLB              | None            |
| Nickel or Dime                   | `T` in `122` or `131`                                                    | NB               | None            |
| Any                              | `Y` in `014`, `113`, `122`, `221`, `113t`, `131`, `212`, `230`, or `023` | SS               | None            |
| `43` front                       | `RB`                                                                     | MLB              | None            |
| Non-`43` front, Weak offense     | `RB`                                                                     | WILB             | None            |
| Non-`43` front, non-Weak offense | `RB`                                                                     | SILB             | None            |
| Any                              | `FB`                                                                     | SLB              | None            |

**Formation breakdown:** the 4-3/3-4 front only changes the RB assignment. Regular/Nickel/Dime changes the `T` assignment. Other listed roles are assigned without a defensive-personnel check.

## Tampa 2

This class uses route groups to assign underneath defenders and, for selected routes, a second defender. `FS` and `SS` below are the code's double/help assignments, not a claim that every Tampa 2 call has identical match rules.

| ----------------------------- | ------------------------------------------------------------------------ | ------------------------ | ------------------------------------- | ------------------ |
| Defensive formation condition | Offensive player / formation                                             | Route                    | Primary                               | Double / help      |
| Any                           | `X(SE)`; `Z(FL)` in `131`; `T` in `221` or `230`                         | Deep In / Post           | MLB                                   | FS                 |
| Any                           | Same outside group                                                       | Short inside             | LCB                                   | WLB                |
| Any                           | Same outside group                                                       | Deep outside / vertical  | LCB                                   | FS                 |
| Any                           | Same outside group                                                       | Flat / short outside     | LCB                                   | None               |
| Any                           | Other `Z(FL)` or `U`                                                     | Deep In / Post           | MLB                                   | FS                 |
| Any                           | Other `Z(FL)` or `U`                                                     | Deep outside / vertical  | RCB                                   | SS                 |
| `43` front                    | Other `Z(FL)` or `U`                                                     | Short inside             | MLB                                   | None               |
| Non-`43` front                | Other `Z(FL)` or `U`                                                     | Short inside             | SILB                                  | None               |
| Regular                       | Other `Z(FL)` or `U`                                                     | Flat / short outside     | SLB                                   | None               |
| Non-Regular                   | Other `Z(FL)` or `U`                                                     | Flat / short outside     | RCB                                   | None               |
| Any                           | `R` in `014`, `023`, or `113`; or `V`                                    | Deep In / Post           | MLB                                   | FS                 |
| Any                           | Same `R`/`V` group                                                       | Deep outside / vertical  | NB (`R`), DB (`V`)                    | FS                 |
| `43` front                    | Same `R`/`V` group                                                       | Short inside             | MLB                                   | None               |
| Non-`43` front                | Same `R`/`V` group                                                       | Short inside             | WILB                                  | None               |
| `V`                           | Same group                                                               | Flat / short outside     | WLB                                   | None               |
| Regular, non-`V`              | Same group                                                               | Flat / short outside     | WLB                                   | None               |
| Non-Regular, non-`V`          | Same group                                                               | Flat / short outside     | NB                                    | None               |
| Any                           | `R` in `005`, `014t`, `113t`, or `203`; or `S`                           | Deep In / Post           | MLB                                   | FS                 |
| Any                           | Same `R`/`S` group                                                       | Deep outside / vertical  | NB (`R`), RCB (`S`)                   | SS (`R`), SS (`S`) |
| `43` front                    | Same `R`/`S` group                                                       | Short inside             | MLB                                   | None               |
| Non-`43` front                | Same `R`/`S` group                                                       | Short inside             | SILB                                  | None               |
| Regular, `S`                  | Same group                                                               | Flat / short outside     | SLB                                   | None               |
| Non-Regular, `S`              | Same group                                                               | Flat / short outside     | RCB                                   | None               |
| `R` in the same group         | Same group                                                               | Flat / short outside     | NB                                    | None               |
| Any                           | `Y` in `014t`; or `T` in `023`, `122`, or `131`                          | Deep In / Post           | MLB                                   | FS                 |
| Any                           | Same `Y`/`T` group                                                       | Deep outside / vertical  | FS                                    | None               |
| `43` front                    | Same `Y`/`T` group                                                       | Short inside             | MLB                                   | None               |
| Non-`43` front                | Same `Y`/`T` group                                                       | Short inside             | WLB                                   | None               |
| Any                           | Same `Y`/`T` group                                                       | Flat / short outside     | WLB                                   | None               |
| `43` front                    | `Y` in `014`, `113`, `122`, `221`, `113t`, `131`, `212`, `230`, or `023` | Underneath               | SLB                                   | None               |
| `34` front, Dime              | Same `Y` group                                                           | Underneath               | SLB                                   | None               |
| `34` front, non-Dime          | Same `Y` group                                                           | Underneath               | SILB                                  | None               |
| Any front                     | Same `Y` group                                                           | Deep In / Post           | SLB (`43`), SILB (otherwise)          | MLB                |
| Any                           | Same `Y` group                                                           | Deep outside / vertical  | SS                                    | None               |
| Any                           | `RB`                                                                     | Deep In / Post           | WLB (Weak offense), SLB (otherwise)   | MLB                |
| Any                           | `RB`                                                                     | Deep outside / vertical  | FS (Weak offense), SS (otherwise)     | None               |
| `43` front                    | `RB`                                                                     | Short inside             | WLB (Weak offense), SLB (otherwise)   | None               |
| Non-`43` front                | `RB`                                                                     | Short inside             | WILB (Weak offense), SILB (otherwise) | None               |
| Any                           | `RB`                                                                     | Flat / short outside     | WLB (Weak offense), SLB (otherwise)   | None               |
| Any                           | `RB`                                                                     | Other/unrecognized route | WILB (Weak offense), SILB (otherwise) | None               |
| `43` front, short inside      | `FB`                                                                     | Short inside             | MLB                                   | None               |
| Other                         | `FB`                                                                     | Any route                | SLB                                   | None               |

**Formation breakdown:** branches commonly differ on `43` versus non-`43`, and sometimes on Regular versus Nickel/Dime. `34` is only explicitly checked in the second `Y` group; an unmatched front/personnel can leave that player's assignment unset.

## Cover 1

The primary assignment is route-independent and follows the Man Coverage table. The exception is deep-inside routes: `6 Deep In (13-18)` and `8 Post (19-26)` also get `FS` as the double/help defender.

| ----------------------------------------------------------- | ------------------------------------ | ---------------------------- | ------------- |
| Defensive formation condition                               | Offensive player / formation         | Primary defender             | Double / help |
| Same position and offensive-formation rules as Man Coverage | All supported routes                 | Same primary as Man Coverage | None          |
| Any                                                         | Any receiver running Deep In or Post | Unchanged                    | FS            |

The front and personnel effects are the same as Man Coverage: `43` changes the RB assignment, and Regular/Nickel/Dime changes some `T` assignments.

## Cover 2

| ------------------------------------ | ----------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------------- | ----------------------------------- |
| Defensive formation condition        | Offensive player / formation                                                                          | Route                              | Primary                               | Double / help                       |
| Any                                  | `X(SE)`; `Z(FL)` in `131`; `T` in `221` or `230`                                                      | Any                                | LCB                                   | None                                |
| Any                                  | Other `Z(FL)` or `U`                                                                                  | Any                                | RCB                                   | None                                |
| Any                                  | `R` in `014`, `023`, or `113`                                                                         | Any                                | NB                                    | None                                |
| Any                                  | `S` in `005`, `014t`, `113t`, or `203`                                                                | Any                                | DB                                    | None                                |
| Any                                  | `R` in `005`, `014t`, `113t`, or `203`                                                                | Any                                | NB                                    | None                                |
| Any                                  | `V`                                                                                                   | Any                                | None                                  | None except deep-outside help below |
| `43` front                           | `Y` in `014t`; or `T` in `023`, `122`, or `131`                                                       | Flat/short outside or short inside | MLB                                   | None                                |
| Non-`43` front                       | Same `Y`/`T` group                                                                                    | Flat/short outside or short inside | SILB                                  | None                                |
| Regular or Nickel                    | Same `Y`/`T` group                                                                                    | Deep routes                        | WLB (`43`), SILB (`34`)               | None                                |
| Dime / other non-Regular, non-Nickel | Same `Y`/`T` group                                                                                    | Deep routes                        | MLB (`43`), WLB (otherwise)           | None                                |
| `43` front                           | `Y` in `014`, `113`, `122`, `221`, `113t`, `131`, `212`, `230`, or `023`                              | Short routes                       | MLB                                   | None                                |
| Non-`43` front                       | Same `Y` group                                                                                        | Short routes                       | SLB                                   | None                                |
| Regular or Nickel                    | Same `Y` group                                                                                        | Deep routes                        | MLB (`43`), SILB (`34`)               | None                                |
| Dime / other non-Regular, non-Nickel | Same `Y` group                                                                                        | Deep routes                        | MLB (`43`), SLB (otherwise)           | None                                |
| `43` front                           | `RB`                                                                                                  | Any                                | MLB                                   | None                                |
| Non-`43` front                       | `RB`                                                                                                  | Short routes                       | SLB                                   | None                                |
| Non-`43` front                       | `RB`                                                                                                  | Other routes                       | WILB (Weak offense), SILB (otherwise) | None                                |
| Any                                  | `FB`                                                                                                  | Any                                | SLB                                   | None                                |
| Any                                  | Deep outside / vertical route by an outside group, `V`, selected `T`/`R` formations, or `Y` in `014t` | Deep outside / vertical            | Primary above, if one was assigned    | FS for listed groups; SS otherwise  |

The final help rule applies only to `5 Deep Out`, `7 Corner`, `9 Fade`, and `D Deep Fade`; it does not include Wheel. The `V` primary remains `None` even when the deep-route rule adds a help defender.

**Formation breakdown:** the front (`43`/`34`) changes linebacker choices. Regular/Nickel/Dime changes `Y`/`T` deep-route assignments. Outside receiver and slot assignments are mostly formation-independent, apart from the selected double/help rule.

## Cover 3 Cloud

The code treats `X(SE)` and selected `Z(FL)`/`T` formations as the cloud-side outside receiver. For those routes, the primary is LCB; the route-specific second assignment is shown below.

| ----------------------------- | ---------------------------- | ---------------------------------------- | ------------------------------------------ | ----------------------------------- |
| Defensive formation condition | Offensive player / formation | Route                                    | Primary                                    | Double / help                       |
| Regular                       | Cloud-side outside group     | Screen, Flat, Out, Comeback              | LCB                                        | WLB                                 |
| Non-Regular                   | Cloud-side outside group     | Screen, Flat, Out, Comeback              | LCB                                        | None                                |
| `43` front                    | Cloud-side outside group     | Dig, Slant, Curl                         | LCB                                        | MLB (Regular/Dime), WLB (otherwise) |
| `34` front                    | Cloud-side outside group     | Dig, Slant, Curl                         | LCB                                        | WLB (Nickel/Dime), WILB (otherwise) |
| Regular                       | Cloud-side outside group     | Deep Out, Corner, Fade, Wheel, Deep Fade | LCB                                        | None                                |
| Non-Regular                   | Cloud-side outside group     | Deep Out, Corner, Fade, Wheel, Deep Fade | LCB                                        | NB                                  |
| Any                           | Cloud-side outside group     | Deep In, Post                            | LCB                                        | FS                                  |
| Any                           | Other `Z(FL)` or `U`         | Screen, Flat, Out, Comeback              | SLB (Regular), RCB (otherwise)             | None                                |
| `43` front                    | Other `Z(FL)` or `U`         | Dig, Slant, Curl                         | MLB                                        | None                                |
| `34` front                    | Other `Z(FL)` or `U`         | Dig                                      | SILB (Regular/non-Dime), NB (Dime)         | None                                |
| `34` front                    | Other `Z(FL)` or `U`         | Slant/Curl                               | SILB or SLB depending on Nickel/Dime token | None                                |
| Regular                       | Other `Z(FL)` or `U`         | Deep Out, Corner, Fade, Wheel, Deep Fade | RCB                                        | None                                |
| Non-Regular                   | Other `Z(FL)` or `U`         | Deep Out, Corner, Fade, Wheel, Deep Fade | SS                                         | None                                |
| Regular                       | Other `Z(FL)` or `U`         | Deep In, Post                            | SS                                         | None                                |
| Non-Regular                   | Other `Z(FL)` or `U`         | Deep In, Post                            | FS                                         | None                                |

The remaining slot, tight-end, RB, and FB branches are route-specific and use additional Regular/Nickel/Dime and `43`/`34` checks. Their complete direct mapping is in the `Cover3CloudAssignment.assign()` method. Two notable current behaviors:

- A Weak-offense `RB` on `F Flat (0-4)` raises `NameError` because that branch refers to `def_formation` instead of `self.def_formation`.
- RB route matches are incomplete; unsupported routes return `(None, None)`.

**Formation breakdown:** cloud-side doubles and underneath assignments change with Regular/Nickel/Dime and the `43`/`34` front. Some checks require the literal phrase `Nickel Personnel` or `Dime Personnel`, while others only check `Nickel` or `Dime`.

## Cover 3 Sky

Cover 3 Sky is heavily route- and formation-dependent. It returns a primary defender but does not assign a second defender in this class.

| ----------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Defensive formation condition | Offensive player / formation                                             | Route behavior                                                                                                                                                                                                                             |
| Any                           | `X(SE)`; `Z(FL)` in `131`; `T` in `221` or `230`                         | Flats/screens/outs/comebacks: WLB in Regular, otherwise LCB. Short inside: `43`/`34` plus personnel choose MLB/WLB/WILB. Deep outside: LCB in Regular, otherwise NB. Deep In/Post: FS.                                                     |
| Any                           | Other `Z(FL)` or `U`                                                     | Flats and short outside: SLB in Regular; otherwise RCB, with Nickel-specific SS/SLB exceptions. Short inside: mostly MLB in `43`, SILB/SLB/SS by front and personnel. Deep outside: RCB in Regular/Nickel, otherwise DB. Deep In/Post: FS. |
| Any                           | `R` in `014`, `023`, or `113`                                            | Underneath: generally WLB/MLB/WILB by front and personnel. Deep outside: FS in Regular, NB in Nickel, DB in Dime. Deep In/Post: FS.                                                                                                        |
| Any                           | `R` in `005`, `014t`, `113t`, or `203`; or `S`                           | Underneath: SLB/SS/MLB/SILB by route, front, and package. Deep outside: RCB in Regular/Nickel, otherwise DB. Deep In/Post: FS.                                                                                                             |
| Any                           | `Y` in `014t`; `T` in `023`, `122`, or `131`                             | Screens/Flats and short routes: WLB/LCB/MLB/SILB/SS by front and package. Deep outs/corners: LCB in Regular, otherwise NB; deep in/post and selected vertical routes: FS.                                                                  |
| Any                           | `Y` in `014`, `113`, `122`, `221`, `113t`, `131`, `212`, `230`, or `023` | Underneath: SS/SILB/SLB/MLB/RCB by route and package. Deep outs/corners: RCB in Regular/Nickel, otherwise DB. Deep In/Post/Fade/Deep Fade: FS; Wheel and other deep routes vary by package.                                                |
| Any                           | Weak `RB`                                                                | Screen/Flat/Out/Comeback/Wheel: WLB or LCB by package. Dig/Slant/Curl: MLB/WLB/WILB by front and package. Other routes are not handled.                                                                                                    |
| Any                           | Non-Weak `RB`                                                            | Short routes: SLB/SS/MLB by front and package. Wheel: SLB/RCB/SS/RCB by front and package. Other routes are not handled.                                                                                                                   |
| `34` front                    | `FB`                                                                     | Dime: SS; other `34`: SILB                                                                                                                                                                                                                 |
| Non-`34` front                | `FB`                                                                     | Pro formation: MLB in Nickel, otherwise SS. Non-Pro: WLB in Nickel, otherwise MLB.                                                                                                                                                         |

**Formation breakdown:** assignments in this class often test the base front first, then personnel. Conditions do not always cover every combination, especially some `34` Nickel cases. RB route branches omit several deep routes, which therefore return `(None, None)`.

## Cover 4

| ----------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Defensive formation condition | Offensive player / formation                                             | Route behavior                                                                                                                                                                                                           |
| Any                           | `X(SE)`; `Z(FL)` in `131`; `T` in `221` or `230`                         | Screen/Flat/Out/Comeback: WLB in Regular, otherwise LCB. Short inside: MLB in `43`; SILB in `34` Regular/Nickel, otherwise SLB. Deep outs/corners/fades: LCB in Regular, otherwise NB. Deep In/Post: FS.                 |
| Any                           | Other `Z(FL)` or `U`                                                     | Underneath: SLB, MLB, or SILB by route and `43`/`34`/personnel. Deep outside: RCB in Regular/Nickel, otherwise DB. Deep In/Post: SS. Wheel: MLB in `43`; otherwise SILB in Regular/Nickel, SLB otherwise.                |
| Any                           | `R` in `014`, `023`, or `113`                                            | Underneath: WLB/MLB/SILB/SLB by route and front. Deep outside: LCB in Regular, otherwise NB. Deep In/Post: FS.                                                                                                           |
| Any                           | `R` in `005`, `014t`, `113t`, or `203`; or `S`                           | Underneath: SLB/MLB/SILB by route and front. Deep outside: RCB in Regular/Nickel, otherwise DB. Deep In/Post: SS.                                                                                                        |
| Any                           | `Y` in `014t`; `T` in `023`, `122`, or `131`                             | Underneath: WLB/LCB/MLB/SILB/SLB by route and front/package. Deep outs/corners: LCB in Regular, otherwise NB. Deep In/Post and most listed vertical routes: FS.                                                          |
| Any                           | `Y` in `014`, `113`, `122`, `221`, `113t`, `131`, `212`, `230`, or `023` | Underneath: SLB/MLB/WLB/SILB by route and front/personnel. Deep outs/corners: RCB in Regular/Nickel, otherwise DB. Deep In/Post: FS/SS. Fade, Deep Fade, and Wheel: commonly SS, with route-specific package exceptions. |
| Any                           | Weak `RB`                                                                | Screen/Flat/Out/Comeback/Wheel: WLB in Regular, otherwise LCB. Dig/Slant/Curl: MLB/WILB/WLB by front/personnel. Other routes are not handled.                                                                            |
| Any                           | Non-Weak `RB`                                                            | Short routes: SLB/MLB/WLB/SILB/RCB by front and package. Wheel: SLB/RCB/MLB by front and package. Other routes are not handled.                                                                                          |
| `43` front                    | `FB`                                                                     | WLB in Nickel; otherwise MLB                                                                                                                                                                                             |
| Non-`43` front                | `FB`                                                                     | Pro: SLB in Dime, otherwise SILB. Non-Pro: WILB in Regular, otherwise WLB.                                                                                                                                               |

**Formation breakdown:** the code branches on `43` versus non-`43` in most underneath assignments. `34` checks and Regular/Nickel/Dime checks further change linebacker or defensive-back choices. The RB route cases are incomplete, so deep routes not explicitly listed in those branches return `(None, None)`.

## Press 1

The primary assignment is route-independent and follows the Man Coverage table. For `6 Deep In (13-18)` and `8 Post (19-26)`, the class also assigns FS as the double/help defender.

| ----------------------------------------------------------- | ------------------------------------ | ---------------------------- | ------------- |
| Defensive formation condition                               | Offensive player / formation         | Primary defender             | Double / help |
| Same position and offensive-formation rules as Man Coverage | All supported routes                 | Same primary as Man Coverage | None          |
| Any                                                         | Any receiver running Deep In or Post | Unchanged                    | FS            |

The class comment calls this bump-and-run coverage, but its assignment method does not otherwise distinguish press technique by route.

## Press 2

The base primary mapping is similar to Man Coverage, with different treatment for `V` and the `Y`/`T` tight-end groups. Deep-outside routes add a safety assignment.

| -------------------------------- | ------------------------------------------------------------------------------------------------------- | --------------------------------- | ----------------------------------------------------------- | ----------------------------------- |
| Defensive formation condition    | Offensive player / formation                                                                            | Route                             | Primary                                                     | Double / help                       |
| Any                              | `X(SE)`; `Z(FL)` in `131`; `T` in `221` or `230`                                                        | Any                               | LCB                                                         | None                                |
| Any                              | Other `Z(FL)` or `U`                                                                                    | Any                               | RCB                                                         | None                                |
| Any                              | `R` in `014`, `023`, or `113`                                                                           | Any                               | NB                                                          | None                                |
| Any                              | `V`                                                                                                     | Any                               | None                                                        | None except deep-outside help below |
| Any                              | `R` in `005`, `014t`, `113t`, or `203`                                                                  | Any                               | NB                                                          | None                                |
| Any                              | `S` in `005`, `014t`, `113t`, or `203`                                                                  | Any                               | DB                                                          | None                                |
| Any                              | `Y` in `014t`; or `T` in `023`, `122`, or `131`                                                         | Any                               | WLB in Regular/Nickel; otherwise MLB in `43`, WLB otherwise | None                                |
| Regular or Nickel, `43` front    | `Y` in the other listed formations                                                                      | Any                               | MLB                                                         | None                                |
| Regular or Nickel, `34` front    | Same `Y` group                                                                                          | Any                               | SILB                                                        | None                                |
| Other personnel, `43` front      | Same `Y` group                                                                                          | Any                               | MLB                                                         | None                                |
| Other personnel, non-`43` front  | Same `Y` group                                                                                          | Any                               | SLB                                                         | None                                |
| `43` front                       | `RB`                                                                                                    | Any                               | MLB                                                         | None                                |
| Non-`43` front, Weak offense     | `RB`                                                                                                    | Any                               | WILB                                                        | None                                |
| Non-`43` front, non-Weak offense | `RB`                                                                                                    | Any                               | SILB                                                        | None                                |
| Any                              | `FB`                                                                                                    | Any                               | SLB                                                         | None                                |
| Any                              | Deep outside / vertical route by the listed outside, `V`, selected `T`/`R` formations, or `Y` in `014t` | Deep Out, Corner, Fade, Deep Fade | Primary above, if assigned                                  | FS for listed groups; SS otherwise  |

The deep-outside help rule does not include Wheel. `V` has no primary defender even when a help defender is assigned.

**Formation breakdown:** `43`/non-`43` controls RB and some TE assignments. Regular/Nickel versus other personnel changes the second `Y` group. Outside assignments otherwise do not depend on defensive package.

## Current Limitations to Keep in Mind

- A `None` primary means the code did not select a defender position; it is not the same as a defender being assigned to a zone.
- A double/help position is only returned as a position. It does not confirm that a player in that role is present or that the defense's actual call uses that responsibility.
- Several branches depend on precise offensive formation tokens and inconsistent spacing (for example `014 ` versus `014t`).
- Some assignments vary by game-log role mapping: `R`, `S`, and `V` represent the first, second, and third slot receivers; `Y`, `T`, and `U` represent the first, second, and third tight ends.
- The current tests mainly check that methods return tuples. They do not validate most position/route/formation combinations.

For exact branch-level behavior, see [`coverage_assignments.py`](coverage_assignments.py). The player-position resolution happens in [`game_service.py`](game_service.py).
