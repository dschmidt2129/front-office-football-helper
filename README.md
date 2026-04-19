# Front Office Football 8 Helper

A comprehensive PyQt5-based analysis tool that parses and processes game logs from **Front Office Football 8** (FOF8), providing detailed insights into offensive and defensive play personnel, formations, route assignments, and coverage schemes.

## Overview

This application automates the analysis of FOF8 game simulations by:
- Extracting and cleaning play data from game logs
- Identifying offensive and defensive personnel for each play
- Analyzing receiver routes and targeting information
- Determining defensive coverage assignments based on formations and routes
- Generating CSV reports for further analysis

## Key Features

### 1. **Game Log Processing**
- Parses HTML-formatted game logs from FOF8 installations
- Cleans and filters unwanted plays (penalties, kickoffs, punts, etc.)
- Caches game data for efficient repeated access
- Supports real-time UI updates during processing

### 2. **Play Analysis**
- Extracts player names and actions from play descriptions
- Identifies offensive and defensive formations
- Tracks receiver routes (9 different route types)
- Records targeting, completion, and yardage statistics
- Calculates yards after catch (YAC)

### 3. **Coverage Assignment Intelligence**
Implements multiple defensive coverage schemes:
- **Man Coverage** - Man-to-man defensive assignments
- **Tampa 2** - Two-deep coverage with middle linebacker robber
- **Cover 1** - One-safety coverage with man underneath
- **Cover 2** - Two-safety coverage with cornerback zones
- **Cover 3** - Sky and Cloud variants of three-deep coverage
- **Cover 4** - Four-deep coverage scheme
- **Press** - Press-man coverage variants (Press 1, Press 2)

Coverage logic accounts for:
- Offensive receiver positions (X, Y, Z, R, S, U, V, T, RB, FB)
- Receiver route types and depths
- Offensive formation codes
- Defensive formation types (Regular, Nickel, Dime, 4-3, 3-4)
- Double-team assignments

### 4. **Data Integration**
Leverages FOF8 league data files:
- **player_information.csv** - Player roster and biographical data
- **player_record.csv** - Player team assignments and history
- **team_information.csv** - Team identification and metadata
- **lastboxlog.html** - Complete game play-by-play records

## Application Architecture

### Core Services

#### **GameService** (`game_service.py`)
Orchestrates game log parsing and play analysis:
- Reads and caches HTML game log tables
- Cleans play data by filtering irrelevant plays
- Extracts play descriptions and personnel
- Identifies receivers and pass defenders
- Manages offensive and defensive personnel for each play

#### **PlayerService** (`player_service.py`)
Manages player lookups and roster verification:
- Caches player information and records
- Resolves player IDs from first/last name combinations
- Handles duplicate player names via team filtering
- Tracks player team assignments

#### **TeamService** (`team_service.py`)
Handles team-related queries:
- Maps team names to team IDs
- Verifies player roster membership
- Integrates player and team data

#### **FrontOfficeFootballService** (`front_office_football_service.py`)
High-level orchestration service:
- Coordinates play-by-play processing
- Integrates game service operations
- Manages sequential play analysis workflow
- Handles errors gracefully with logging

#### **CoverageAssignments** (`coverage_assignments.py`)
Defensive coverage assignment engine:
- Base `CoverageAssignments` abstract class
- 9 coverage scheme implementations (Man, Tampa 2, Cover 1-4, Press variants)
- Position-specific and formation-aware routing logic
- Returns primary and double-team defender assignments

### User Interface

#### **FOF8FolderSelector** (`main.py`)
- Folder path selection widget
- Default path suggestion (FOF8 standard installation location)
- Browse dialog for custom installations
- Path validation and display

#### **Home** (Main Window)
- Two-column layout (controls and output)
- Team selector dropdown (32 NFL teams)
- Process Game Files button
- Clear Game Log button
- Real-time output logging text box
- Integrated folder selector component

## Supported Features

### Receiver Route Types
Routes are classified by depth and type:
- **Flat Routes**: Screen, 0-4 yards
- **Short Routes**: Slant, Curl, Comeback, Out (5-12 yards)
- **Deep Routes**: Dig, Post, Corner, Fade, Deep In/Out (13+ yards)
- **Specialized**: Wheel routes, routes beyond 40 yards

### Offensive Formations
Represented by formation codes containing:
- Defensive personnel grouping (e.g., "43", "34")
- Receiving personnel distribution
- Weak/Strong side indicators

### Defensive Formations
Tracked formation types:
- Regular packages
- Nickel (5-DB) packages
- Dime (6-DB) packages
- 4-3 and 3-4 front variations

### Defensive Positions
Comprehensive position tracking:
- Cornerbacks (LCB, RCB)
- Safeties (FS, SS)
- Linebackers (MLB, SILB, WILB, SLB, WLB)
- Nickelback (NB)
- Dime back (DB)

## Data Output

### CSV Report: `receivers_in_game.csv`
Generated file containing receiver-level statistics:
- Player Name
- Position (X, Y, Z, R, S, U, V, T)
- Route Priority (Primary, Secondary, Outlet)
- Route Type
- Targeted? (Boolean)
- Caught? (Boolean)
- Receiving Yards
- Yards After Catch (YAC)
- Passer Name

## Installation & Setup

### Requirements
- Python 3.x
- PyQt5
- pandas
- Front Office Football 8 installation

### Configuration
Update the league identifier in service files if needed:
- Default league ID: `SFL00004`
- Paths: `leaguedata/SFL00004/` and `leagues/SFL00004/`

## Usage

1. Launch the application:
   ```bash
   python main.py
   ```

2. Select or browse to your FOF8 installation folder

3. Choose the team to analyze from the dropdown

4. Click "Process Game Files" to begin analysis

5. Monitor progress in the output log

6. Review `receivers_in_game.csv` for detailed receiver statistics

## Technical Implementation Details

### Error Handling
- Graceful handling of IndexError exceptions
- Generic exception catching for unexpected errors
- Detailed error logging to UI output widget
- Play skipping without interrupting batch processing

### Performance Optimizations
- Single-pass HTML table parsing and caching
- DataFrame caching for player/team lookups
- Avoided redundant file I/O operations
- Real-time UI updates via `QApplication.processEvents()`

### Data Filtering
Automatically removes non-standard plays:
- Kicks (field goals, extra points, kickoffs)
- Punts
- Penalty plays
- Special situations (coin tosses, time-outs, false starts)
- Two-point conversion attempts
- Game start/end markers

## File Structure

```
front-office-football-helper/
├── main.py                           # Application entry point and UI
├── game_service.py                   # Game log parsing and play analysis
├── player_service.py                 # Player lookup and roster management
├── team_service.py                   # Team queries and roster verification
├── front_office_football_service.py  # High-level orchestration
├── coverage_assignments.py           # Defensive coverage scheme logic
├── receivers_in_game.csv             # Generated report (output)
└── build/                            # Build output directory
```

## Future Enhancement Opportunities

- Pass rush assignment tracking
- Run defense personnel analysis
- Defensive coordinator scheme identification
- Statistical comparison across coverage types
- Interactive visualization of play charts
- Season-wide aggregate statistics
- Machine learning-based coverage prediction
- Export to additional formats (Excel, JSON)

## Notes

- Faulthandler is enabled for debugging assistance
- All service classes implement data caching for performance
- UI updates are throttled to prevent freezing during batch operations
- Coverage logic accounts for 10+ formation variations per scheme
- Team roster validation prevents cross-team player name conflicts

## License

This project is created for Front Office Football 8 analysis purposes.

## Support

For issues or questions, consult the inline code documentation and error messages in the application output log.
