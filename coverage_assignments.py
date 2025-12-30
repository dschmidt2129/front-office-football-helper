class CoverageAssignments:
    def __init__(self, route, off_position, off_formation, def_formation):
        self.route = route
        self.off_position = off_position
        self.off_formation = off_formation
        self.def_formation = def_formation

    def assign(self):
        # returns a tuple of (primary_defender, double_team_defender)
        # double_team_defender can be None
        raise NotImplementedError("Subclasses should implement this method")
    
class ManCoverageAssignment(CoverageAssignments):
    # sub class of coverage assignments for man to man coverage
    def assign(self):
        prim_assigned = None
        if(self.off_position == 'X(SE)' or 
            (self.off_position == 'Z(FL)' and '131' in self.off_formation)
            or (self.off_position == 'T' and '221' in self.off_formation)
            or (self.off_position == 'T' and '230' in self.off_formation)):
            prim_assigned = 'LCB'
        elif (self.off_position == 'Z(FL)' or self.off_position == 'U'):
            prim_assigned = 'RCB'
        elif (self.off_position == 'R' and '014' in self.off_formation or
            self.off_position == 'R' and '023' in self.off_formation or
            self.off_position == 'R' and '113' in self.off_formation or
            self.off_position == 'V'):
            if(self.off_position == 'V'):
                prim_assigned = 'SS'
            else:
                prim_assigned = 'NB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
            self.off_position == 'R' and '014t' in self.off_formation or
            self.off_position == 'R' and '113t' in self.off_formation or
            self.off_position == 'R' and '203' in self.off_formation or
            self.off_position == 'S'
            ):
            if self.off_position == 'R':
                prim_assigned = 'NB'
            else:
                prim_assigned = 'DB'
        elif ((self.off_position == 'Y' and '014t' in self.off_formation) or 
            (self.off_position == 'T' and '023' in self.off_formation) or
            (self.off_position == 'T' and '122' in self.off_formation) or
            (self.off_position == 'T' and '131' in self.off_formation)
            ):
            if self.off_position == 'Y':
                prim_assigned = 'SS'
            else:
                if 'Regular' in self.def_formation:
                    prim_assigned = 'WLB'
                elif 'Nickel' in self.def_formation or 'Dime' in self.def_formation:
                    if '023' in self.off_formation:
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'NB'
        elif ((self.off_position == 'Y' and '014 ' in self.off_formation) or
            (self.off_position == 'Y' and '113 ' in self.off_formation) or
            (self.off_position == 'Y' and '122' in self.off_formation) or
            (self.off_position == 'Y' and '221' in self.off_formation) or
            (self.off_position == 'Y' and '113t' in self.off_formation) or
            (self.off_position == 'Y' and '131' in self.off_formation) or
            (self.off_position == 'Y' and '212' in self.off_formation) or
            (self.off_position == 'Y' and '230' in self.off_formation) or
            (self.off_position == 'Y' and '023' in self.off_formation)
            ):
            prim_assigned = 'SS'
        elif self.off_position == 'RB':
            if '43' in self.def_formation:
                prim_assigned = 'MLB'
            else:
                if 'Weak' in self.def_formation:
                    prim_assigned = 'WILB'
                else:
                    prim_assigned = 'SILB' 
        elif self.off_position == 'FB':
            prim_assigned = 'SLB'
        else:
            raise ValueError('coverage assignment not found for route')
        return prim_assigned, None

class Tampa2Assignment(CoverageAssignments):
    # sub class of coverage assignments for Tampa 2 coverage
    def assign(self):
        prim_assigned = None
        doub_assigned = None

        # =========================================================
        # OUTSIDE RECEIVERS (X / Z wide)
        # Corners play short zones (flat / cloud)
        # =========================================================
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):

            prim_assigned = 'LCB'

            match self.route:
                case 'S Screen (S)' | 'F Flat (0-4)':
                    doub_assigned = 'WLB' if 'Regular' in self.def_formation else 'LCB'

                case '0 Dig (0-4)' | '2 Slant (5-8)' | '4 Curl (9-12)':
                    if '43' in self.def_formation:
                        doub_assigned = 'MLB'
                    else:
                        doub_assigned = 'SILB'

                case '1 Out (5-8)' | '3 Comeback (9-12)':
                    doub_assigned = 'WLB' if 'Regular' in self.def_formation else 'LCB'

                # Corner sinks only on deep outside
                case '5 Deep Out (13-18)' | '7 Corner (19-26)' | '9 Fade (27-39)' | 'D Deep Fade (40+)':
                    doub_assigned = 'LCB'

                # Inside breaking verticals → Tampa MLB
                case '6 Deep In (13-18)' | '8 Post (19-26)':
                    prim_assigned = 'MLB' if '43' in self.def_formation else 'SILB'
                    doub_assigned = 'FS'

                case 'W Wheel (9-18)':
                    doub_assigned = 'LCB'

        # =========================================================
        # Z / SLOT / U RECEIVER
        # =========================================================
        elif self.off_position == 'Z(FL)' or self.off_position == 'U':

            match self.route:
                case 'S Screen (S)' | 'F Flat (0-4)':
                    if 'Regular' in self.def_formation:
                        prim_assigned = 'SLB'
                    else:
                        prim_assigned = 'RCB'

                case '0 Dig (0-4)' | '2 Slant (5-8)' | '4 Curl (9-12)':
                    if '43' in self.def_formation:
                        prim_assigned = 'MLB'
                    else:
                        prim_assigned = 'SILB'

                case '1 Out (5-8)' | '3 Comeback (9-12)':
                    if 'Regular' in self.def_formation:
                        prim_assigned = 'SLB'
                    else:
                        prim_assigned = 'RCB'

                case '5 Deep Out (13-18)' | '7 Corner (19-26)':
                    prim_assigned = 'RCB'

                # Slot seam = Tampa signature
                case '6 Deep In (13-18)' | '8 Post (19-26)' | '9 Fade (27-39)':
                    prim_assigned = 'MLB' if '43' in self.def_formation else 'SILB'
                    doub_assigned = 'FS'

                case 'W Wheel (9-18)':
                    prim_assigned = 'RCB'

        # =========================================================
        # BACKFIELD RECEIVERS (R / V)
        # =========================================================
        elif (self.off_position == 'R' and '014 ' in self.off_formation or
              self.off_position == 'R' and '023' in self.off_formation or
              self.off_position == 'R' and '113 ' in self.off_formation or
              self.off_position == 'V'):

            match self.route:
                case 'S Screen (S)' | 'F Flat (0-4)':
                    prim_assigned = 'WLB' if 'Regular' in self.def_formation else 'NB'

                case '0 Dig (0-4)' | '2 Slant (5-8)':
                    prim_assigned = 'MLB' if '43' in self.def_formation else 'WILB'

                case '1 Out (5-8)' | '3 Comeback (9-12)':
                    prim_assigned = 'WLB' if 'Regular' in self.def_formation else 'NB'

                case '4 Curl (9-12)':
                    prim_assigned = 'MLB' if '43' in self.def_formation else 'WILB'

                # RB wheel → MLB carry with safety overlap
                case 'W Wheel (9-18)':
                    prim_assigned = 'MLB'
                    doub_assigned = 'FS'

                case '5 Deep Out (13-18)' | '7 Corner (19-26)' | '9 Fade (27-39)':
                    prim_assigned = 'FS'

        # =========================================================
        # STRONG BACK / S
        # =========================================================
        elif (self.off_position == 'R' and '005' in self.off_formation or
              self.off_position == 'R' and '014t' in self.off_formation or
              self.off_position == 'R' and '113t' in self.off_formation or
              self.off_position == 'R' and '203' in self.off_formation or
              self.off_position == 'S'):

            match self.route:
                case 'S Screen (S)' | 'F Flat (0-4)':
                    prim_assigned = 'SLB' if 'Regular' in self.def_formation else 'RCB'

                case '0 Dig (0-4)' | '2 Slant (5-8)' | '4 Curl (9-12)':
                    prim_assigned = 'MLB' if '43' in self.def_formation else 'SILB'

                case '1 Out (5-8)' | '3 Comeback (9-12)':
                    prim_assigned = 'SLB' if 'Regular' in self.def_formation else 'RCB'

                case '5 Deep Out (13-18)' | '7 Corner (19-26)':
                    prim_assigned = 'RCB'

                case '6 Deep In (13-18)' | '8 Post (19-26)':
                    prim_assigned = 'MLB'
                    doub_assigned = 'FS'

        # =========================================================
        # INLINE / FLEX TE (Y / T)
        # =========================================================
        elif (self.off_position == 'Y' or self.off_position == 'T'):
            match self.route:
                case 'S Screen (S)' | 'F Flat (0-4)':
                    prim_assigned = 'SLB'

                case '0 Dig (0-4)' | '2 Slant (5-8)' | '4 Curl (9-12)':
                    prim_assigned = 'MLB' if '43' in self.def_formation else 'SILB'

                case '1 Out (5-8)' | '3 Comeback (9-12)':
                    prim_assigned = 'SLB'

                # TE seam → Tampa MLB
                case '6 Deep In (13-18)' | '8 Post (19-26)':
                    prim_assigned = 'MLB'
                    doub_assigned = 'FS'

                case '5 Deep Out (13-18)' | '7 Corner (19-26)':
                    prim_assigned = 'FS'

        return prim_assigned, doub_assigned


class Cover1Assignment(CoverageAssignments):
    # sub class of coverage assignments for cover 1 coverage
    def assign(self):
        prim_assigned = None
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):
            prim_assigned = 'LCB'
        elif (self.off_position == 'Z(FL)' or self.off_position == 'U'):
            prim_assigned = 'RCB'
        elif (self.off_position == 'R' and '014' in self.off_formation or
            self.off_position == 'R' and '023' in self.off_formation or
            self.off_position == 'R' and '113' in self.off_formation or
            self.off_position == 'V'):
            if self.off_position == 'V':
                prim_assigned = 'SS'
            else:
                prim_assigned = 'NB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
                self.off_position == 'R' and '014t' in self.off_formation or
                self.off_position == 'R' and '113t' in self.off_formation or
                self.off_position == 'R' and '203' in self.off_formation or
                self.off_position == 'S'
                ):
                if self.off_position == 'R':
                    prim_assigned = 'NB' 
                else:
                    prim_assigned = 'DB'
        elif (self.off_position == 'Y' and '014t' in self.off_formation or 
            (self.off_position == 'T' and '023' in self.off_formation) or
            (self.off_position == 'T' and '122' in self.off_formation) or
            (self.off_position == 'T' and '131' in self.off_formation)
            ):
            if self.off_position == 'Y':
                prim_assigned = 'SS'
            elif self.off_position == 'T':
                if 'Regular' in self.def_formation:
                    prim_assigned = 'WLB'
                elif 'Nickel' in self.def_formation or 'Dime' in self.def_formation:
                    if '023' in self.off_formation:
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'NB'
            # todo: check to see if additional coverages are needed here
        elif ((self.off_position == 'Y' and '014 ' in self.off_formation) or
                (self.off_position == 'Y' and '113 ' in self.off_formation) or
                (self.off_position == 'Y' and '122' in self.off_formation) or
                (self.off_position == 'Y' and '221' in self.off_formation) or
                (self.off_position == 'Y' and '113t' in self.off_formation) or
                (self.off_position == 'Y' and '131' in self.off_formation) or
                (self.off_position == 'Y' and '212' in self.off_formation) or
                (self.off_position == 'Y' and '230' in self.off_formation) or
                (self.off_position == 'Y' and '023' in self.off_formation)
                ):
            prim_assigned = 'SS'
        elif self.off_position == 'RB':
            if '43' in self.def_formation:
                prim_assigned = 'MLB'
            else:
                if 'Weak' in self.def_formation:
                    prim_assigned = 'WILB'
                else:
                    prim_assigned = 'SILB'
        elif self.off_position == 'FB':
            prim_assigned = 'SLB'
        return prim_assigned, None

class Cover2Assignment(CoverageAssignments):
    # sub class of coverage assignments for cover 2 coverage
    def assign(self):
        prim_assigned = None
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):
            prim_assigned = 'LCB'
        elif (self.off_position == 'Z(FL)' or self.off_position == 'U'):
            prim_assigned = 'RCB'
        elif (self.off_position == 'R' and '014 ' in self.off_formation or
                self.off_position == 'R' and '023' in self.off_formation or
                self.off_position == 'R' and '113 ' in self.off_formation or
                self.off_position == 'V'
                ):
            if self.off_position == 'V':
                prim_assigned = None
            else:
                prim_assigned = 'NB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
                self.off_position == 'R' and '014t' in self.off_formation or
                self.off_position == 'R' and '113t' in self.off_formation or
                self.off_position == 'R' and '203' in self.off_formation or
                self.off_position == 'S'
                ):
                if self.off_position == 'R':
                    prim_assigned = 'NB' 
                else:
                    prim_assigned = 'DB'
        elif ((self.off_position == 'Y' and '014t' in self.off_formation) or 
            (self.off_position == 'T' and '023' in self.off_formation) or
            (self.off_position == 'T' and '122' in self.off_formation) or
            (self.off_position == 'T' and '131' in self.off_formation)
            ):
            if('Regular' in self.def_formation or 'Nickel' in self.def_formation):
                prim_assigned = 'WLB'
            else:   
                if ('43' in self.def_formation):
                    prim_assigned = 'MLB'
                elif ('34' in self.def_formation):
                    prim_assigned = 'WLB'
        elif ((self.off_position == 'Y' and '014 ' in self.off_formation) or
                (self.off_position == 'Y' and '113 ' in self.off_formation) or
                (self.off_position == 'Y' and '122' in self.off_formation) or
                (self.off_position == 'Y' and '221' in self.off_formation) or
                (self.off_position == 'Y' and '113t' in self.off_formation) or
                (self.off_position == 'Y' and '131' in self.off_formation) or
                (self.off_position == 'Y' and '212' in self.off_formation) or
                (self.off_position == 'Y' and '230' in self.off_formation) or
                (self.off_position == 'Y' and '023' in self.off_formation)
                ):
                    if('Regular' in self.def_formation or 'Nickel' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'SLB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'SILB'
                    else:
                        if '43' in self.def_formation:
                            prim_assigned = 'MLB'
                        else:
                            prim_assigned = 'SLB'
        elif self.off_position == 'RB':
            if '43' in self.def_formation:
                prim_assigned = 'MLB'
            else:
                if 'Weak' in self.off_formation:
                    prim_assigned = 'WILB'
                else:
                    prim_assigned = 'SILB'
        elif self.off_position == 'FB':
            prim_assigned = 'SLB'
        return prim_assigned, None

class Cover3CloudAssignment(CoverageAssignments):
    # sub class of coverage assignments for cover 3 cloud coverage
    def assign(self):
        prim_assigned = None
        doub_assigned = None
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):
            prim_assigned = 'LCB'
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        doub_assigned = 'WLB'
                    else:
                        doub_assigned = 'LCB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        doub_assigned = 'WLB'
                    else:
                        doub_assigned = 'LCB'
                case '0 Dig (0-4)':
                    if ('43' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            doub_assigned = 'MLB'                                        
                        elif('Nickel' in self.def_formation):
                            doub_assigned = 'WLB'                                        
                        else:
                            doub_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            doub_assigned = 'WLB'                                        
                        elif('Nickel' in self.def_formation):
                            doub_assigned = 'WLB'                                        
                        else:
                            doub_assigned = 'WILB'
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation):
                        doub_assigned = 'WLB'
                    else:
                        doub_assigned = 'LCB'
                case '2 Slant (5-8)':
                    if ('43' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            doub_assigned = 'MLB'                                        
                        elif('Nickel' in self.def_formation):
                            doub_assigned = 'WLB'                                        
                        else:
                            doub_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            doub_assigned = 'WLB'                                        
                        elif('Nickel' in self.def_formation):
                            doub_assigned = 'WLB'                                        
                        else:
                            doub_assigned = 'WILB'
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation):
                        doub_assigned = 'WLB'                                    
                    else:
                        doub_assigned = 'LCB'
                case '4 Curl (9-12)':
                    if ('43' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            doub_assigned = 'MLB'                                        
                        elif('Nickel' in self.def_formation):
                            doub_assigned = 'WLB'                                        
                        else:
                            doub_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            doub_assigned = 'WLB'                                        
                        elif('Nickel' in self.def_formation):
                            doub_assigned = 'WLB'                                        
                        else:
                            doub_assigned = 'WILB'
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        doub_assigned = 'LCB'
                    else:
                        doub_assigned = 'NB'
                case '6 Deep In (13-18)':
                    doub_assigned = 'FS'
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        doub_assigned = 'LCB'
                    else:
                        doub_assigned = 'NB'
                case '8 Post (19-26)':
                    doub_assigned = 'FS'
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        doub_assigned = 'LCB'
                    else:
                        doub_assigned = 'NB'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        doub_assigned = 'LCB'
                    else:
                        doub_assigned = 'NB'
                case 'D Deep Fade (40+)':
                    if ('Regular' in self.def_formation):
                        doub_assigned = 'LCB'
                    else:
                        doub_assigned = 'NB'
        elif (self.off_position == 'Z(FL)' or self.off_position == 'U'):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '0 Dig (0-4)':
                    if ('Regular' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'MLB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'SILB'
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'NB'                            
                        else:
                            prim_assigned = 'SILB'
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '2 Slant (5-8)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Nickel' in self.def_formation or 'Dime' in self.def_formation):
                            prim_assigned = 'SLB'                            
                        else:
                            prim_assigned = 'SILB'
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '4 Curl (9-12)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                            prim_assigned = 'SLB'                            
                        else:
                            prim_assigned = 'SILB'
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    else:
                        prim_assigned = 'SS'
                case '6 Deep In (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    else:
                        prim_assigned = 'FS'
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    else:
                        prim_assigned = 'SS'
                case '8 Post (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    else:
                        prim_assigned = 'FS'
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    else:
                        prim_assigned = 'SS'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    else:
                        prim_assigned = 'SS'
                case 'D Deep Fade (40+)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    else:
                        prim_assigned = 'SS'
        elif (self.off_position == 'R' and '014 ' in self.off_formation or
                self.off_position == 'R' and '023' in self.off_formation or
                self.off_position == 'R' and '113 ' in self.off_formation or
                self.off_position == 'V'
                ):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                case '0 Dig (0-4)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'WLB'                            
                        elif ('Nickel' in self.def_formation):
                            prim_assigned = 'SILB'
                        elif ('Regular' in self.def_formation):
                            prim_assigned = 'WILB'
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                case '2 Slant (5-8)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                            
                        elif ('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'SILB'
                        elif ('Regular' in self.def_formation):
                            prim_assigned = 'WILB'
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Dime Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'DB'
                        elif ('34'in self.def_formation):
                            prim_assigned = 'WLB'
                case '4 Curl (9-12)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'WLB'                            
                        elif ('Nickel' in self.def_formation):
                            prim_assigned = 'SILB'
                        elif ('Regular' in self.def_formation):
                            prim_assigned = 'WILB'
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'FS'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case '6 Deep In (13-18)':
                    prim_assigned = 'FS'
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'FS'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case '8 Post (19-26)':
                    prim_assigned = 'FS'
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'FS'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'FS'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case 'D Deep Fade (40+)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'FS'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
                self.off_position == 'R' and '014t' in self.off_formation or
                self.off_position == 'R' and '113t' in self.off_formation or
                self.off_position == 'R' and '203' in self.off_formation or
                self.off_position == 'S'
                ):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'    
                case '0 Dig (0-4)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'NB'                                        
                        else:
                            prim_assigned = 'SILB'
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '2 Slant (5-8)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                            prim_assigned = 'SLB'
                        else:
                            prim_assigned = 'SILB'
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'                                       
                case '4 Curl (9-12)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                            prim_assigned = 'SLB'
                        else:
                            prim_assigned = 'SILB'
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    else:
                        prim_assigned = 'SS'
                case '6 Deep In (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    else:
                        prim_assigned = 'FS'
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    else:
                        prim_assigned = 'SS'
                case '8 Post (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    else:
                        prim_assigned = 'FS'
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    else:
                        prim_assigned = 'SS'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    else:
                        prim_assigned = 'SS'                                   
                case 'D Deep Fade (40+)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    else:
                        prim_assigned = 'SS'
        elif ((self.off_position == 'Y' and '014t' in self.off_formation) or 
                (self.off_position == 'T' and '023' in self.off_formation) or
                (self.off_position == 'T' and '122' in self.off_formation) or
                (self.off_position == 'T' and '131' in self.off_formation)
                ):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Nickel Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'WLB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                case '0 Dig (0-4)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'SILB'
                        else:
                            prim_assigned = 'WILB'
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation or 'Nickel Personnel' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                case '2 Slant (5-8)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'SILB'
                        else:
                            prim_assigned = 'WILB'
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation or 'Nickel Personnel' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Dime Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'DB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'WLB'
                case '4 Curl (9-12)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'SILB'
                        else:
                            prim_assigned = 'WILB'                              
                case '5 Deep Out (13-18)':
                    if('Regular' in self.def_formation):
                        prim_assigned = 'FS'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case '6 Deep In (13-18)':
                    prim_assigned = 'FS'                          
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'FS'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'                               
                case '8 Post (19-26)':
                    prim_assigned = 'FS'
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'FS'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'FS'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'                                   
                case 'D Deep Fade (40+)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'FS'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
        elif ((self.off_position == 'Y' and '014 ' in self.off_formation) or
                (self.off_position == 'Y' and '113 ' in self.off_formation) or
                (self.off_position == 'Y' and '122' in self.off_formation) or
                (self.off_position == 'Y' and '221' in self.off_formation) or
                (self.off_position == 'Y' and '113t' in self.off_formation) or
                (self.off_position == 'Y' and '131' in self.off_formation) or
                (self.off_position == 'Y' and '212' in self.off_formation) or
                (self.off_position == 'Y' and '230' in self.off_formation) or
                (self.off_position == 'Y' and '023' in self.off_formation)
                ):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '0 Dig (0-4)':
                    if('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation or 'Regular' in self.def_formation):
                            prim_assigned = 'SILB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'SLB'
                case '1 Out (5-8)':
                    if('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '2 Slant (5-8)':
                    if('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Regular' in self.def_formation):
                            prim_assigned = 'SILB'                                        
                        elif('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                            prim_assigned = 'SLB'                                        
                case '3 Comeback (9-12)':
                    if('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Dime Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'RCB'
                        elif ('34'in self.def_formation):
                            prim_assigned = 'SLB'                                       
                case '4 Curl (9-12)':
                    if('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation or 'Nickel Personnel' in self.def_formation):
                            prim_assigned = 'SLB'                                        
                        elif('Regular' in self.def_formation):
                            prim_assigned = 'SILB'                                 
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'SS'                                      
                case '6 Deep In (13-18)':
                    if('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'FS'
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'SS'                             
                case '8 Post (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'FS'                                        
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'FS'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        prim_assigned = 'SS'
        return prim_assigned, doub_assigned

class Cover3SkyAssignment(CoverageAssignments):
    # sub class of coverage assignments for cover 3 sky coverage
    def assign(self):
        prim_assigned = None
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'LCB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'LCB'
                case '0 Dig (0-4)':
                    if ('43' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'MLB'                                        
                        elif('Nickel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        elif('Nickel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'WILB'
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'LCB'
                case '2 Slant (5-8)':
                    if ('43' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'MLB'                                        
                        elif('Nickel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        elif('Nickel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'WILB'
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'                                    
                    else:
                        prim_assigned = 'LCB'
                case '4 Curl (9-12)':
                    if ('43' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'MLB'                                        
                        elif('Nickel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        elif('Nickel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'WILB'
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
                case '6 Deep In (13-18)':
                    prim_assigned = 'FS'
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
                case '8 Post (19-26)':
                    prim_assigned = 'FS'
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
                case 'D Deep Fade (40+)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'                                                                      
        elif (self.off_position == 'Z(FL)' or self.off_position == 'U'):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif('Nickel Personnel' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                    elif('Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif('Nickel Personnel' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                    elif('Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '0 Dig (0-4)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SILB'
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif('Nickel Personnel' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                    elif('Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '2 Slant (5-8)':
                    if('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    elif('Nickel Personnel' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'MLB'
                        else:
                            prim_assigned = 'SS'
                    elif('Dime Personnel' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif('Nickel Personnel' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                    elif('Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '4 Curl (9-12)':
                    if('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    elif('Nickel Personnel' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'MLB'
                        else:
                            prim_assigned = 'SS'
                    elif('Dime Personnel' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case '6 Deep In (13-18)':
                    prim_assigned = 'FS'
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case '8 Post (19-26)':
                    prim_assigned = 'FS'
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case 'D Deep Fade (40+)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
        elif (self.off_position == 'R' and '014 ' in self.off_formation or
                self.off_position == 'R' and '023' in self.off_formation or
                self.off_position == 'R' and '113 ' in self.off_formation or
                self.off_position == 'V'
                ):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'LCB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'LCB'
                case '0 Dig (0-4)':
                    if ('43' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'MLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'WILB'
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'LCB'
                case '2 Slant (5-8)':
                    if ('43' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'MLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'WILB'
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'                                    
                    else:
                        prim_assigned = 'LCB'
                case '4 Curl (9-12)':
                    if ('43' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'MLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'WILB'
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
                case '6 Deep In (13-18)':
                    prim_assigned = 'FS'
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
                case '8 Post (19-26)':
                    prim_assigned = 'FS'
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
                case 'D Deep Fade (40+)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
                self.off_position == 'R' and '014t' in self.off_formation or
                self.off_position == 'R' and '113t' in self.off_formation or
                self.off_position == 'R' and '203' in self.off_formation or
                self.off_position == 'S'
                ):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif ('Nickel Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '0 Dig (0-4)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'SS'                                        
                        else:
                            prim_assigned = 'SILB'
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '2 Slant (5-8)':
                    if('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    elif ('Nickel Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'MLB'
                        else:
                            prim_assigned = 'SS'
                    elif ('Dime Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'SLB'
                    elif ('Nickel Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                case '4 Curl (9-12)':
                    if('Regular' in self.def_formation):
                        prim_assigned = 'SS'
                    elif ('Nickel Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'MLB'
                        else:
                            prim_assigned = 'SS'
                    elif ('Dime Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SLB'
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case '6 Deep In (13-18)':
                    prim_assigned = 'FS'
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case '8 Post (19-26)':
                    prim_assigned = 'FS'                                 
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'                                  
                case 'D Deep Fade (40+)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Nickel Personnel' in self.def_formation):
                        prim_assigned = 'RCB'
                    elif ('Dime Personnel' in self.def_formation):
                        prim_assigned = 'DB'
        elif ((self.off_position == 'Y' and '014t' in self.off_formation) or 
                (self.off_position == 'T' and '023' in self.off_formation) or
                (self.off_position == 'T' and '122' in self.off_formation) or
                (self.off_position == 'T' and '131' in self.off_formation)
                ):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'WLB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'WILB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'LCB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'WLB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'WLB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'WILB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'LCB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'WLB'                                   
                case '0 Dig (0-4)':
                    if ('43' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'MLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'MLB'         
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SILB'                   
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'WLB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'WILB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'LCB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'WLB'                                            
                case '2 Slant (5-8)':
                    if ('43' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'MLB'                                        
                        elif('Nickel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'MLB'                                    
                    elif ('34' in self.def_formation):
                        if ('Dime' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SILB'                                    
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'WLB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'WILB'
                    elif ('Nickel Personnel' in self.def_formation or 'Dime Personnel' in self.def_formation):
                        if('43' in self.def_formation):
                            prim_assigned = 'LCB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'WLB'                                                  
                case '4 Curl (9-12)':
                    if ('43' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'MLB'                                        
                        elif('Nickel Personnel' in self.def_formation):
                            prim_assigned = 'WLB'                                        
                        else:
                            prim_assigned = 'MLB'     
                    elif ('34' in self.def_formation):
                        if ('Dime Personnel' in self.def_formation):
                            prim_assigned = 'SS'
                        else:
                            prim_assigned = 'SILB'                                          
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
                case '6 Deep In (13-18)':
                    prim_assigned = 'FS'
                case '7 Corner (19-26)':
                    if('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'
                case '8 Post (19-26)':
                    prim_assigned = 'FS'                                  
                case '9 Fade (27-39)':
                    prim_assigned = 'FS'                             
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    else:
                        prim_assigned = 'NB'                                 
                case 'D Deep Fade (40+)':
                    prim_assigned = 'FS'
        return prim_assigned, None

class Cover4Assignment(CoverageAssignments):
    # sub class of coverage assignments for cover 4 coverage
    def assign(self):
        prim_assigned = None
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):
            match self.route:
                case 'S Screen (S)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'LCB'
                case 'F Flat (0-4)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'LCB'
                case '0 Dig (0-4)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Regular' in self.def_formation or 'Nickel Personnel' in self.def_formation):
                            prim_assigned = 'SILB'
                        elif('Dime Personnel' in self.def_formation):
                            prim_assigned = 'SLB'
                case '1 Out (5-8)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'LCB'
                case '2 Slant (5-8)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Regular' in self.def_formation or 'Nickel Personnel' in self.def_formation):
                            prim_assigned = 'SILB'
                        elif('Dime Personnel' in self.def_formation):
                            prim_assigned = 'SLB'
                case '3 Comeback (9-12)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'LCB'
                case '4 Curl (9-12)':
                    if ('43' in self.def_formation):
                        prim_assigned = 'MLB'
                    elif ('34' in self.def_formation):
                        if ('Regular' in self.def_formation or 'Nickel Personnel' in self.def_formation):
                            prim_assigned = 'SILB'
                        elif('Dime Personnel' in self.def_formation):
                            prim_assigned = 'SLB'
                case '5 Deep Out (13-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    elif('Nickel Personnel' in self.def_formation or'Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                case '6 Deep In (13-18)':
                    prim_assigned = 'FS'
                case '7 Corner (19-26)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    elif('Nickel Personnel' in self.def_formation or'Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                case '8 Post (19-26)':
                    prim_assigned = 'FS'
                case '9 Fade (27-39)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    elif('Nickel Personnel' in self.def_formation or'Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
                case 'W Wheel (9-18)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'WLB'
                    elif('Nickel Personnel' in self.def_formation or'Dime Personnel' in self.def_formation):
                        prim_assigned = 'LCB'
                case 'D Deep Fade (40+)':
                    if ('Regular' in self.def_formation):
                        prim_assigned = 'LCB'
                    elif('Nickel Personnel' in self.def_formation or'Dime Personnel' in self.def_formation):
                        prim_assigned = 'NB'
        return prim_assigned, None

class Press1Assignment(CoverageAssignments):
    # sub class of coverage assignments for bump and run coverage
    def assign(self):
        prim_assigned = None
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):
            prim_assigned = 'LCB'
        elif (self.off_position == 'Z(FL)' or self.off_position == 'U'):
            prim_assigned = 'RCB'
        elif (self.off_position == 'R' and '014' in self.off_formation or
            self.off_position == 'R' and '023' in self.off_formation or
            self.off_position == 'R' and '113' in self.off_formation or
            self.off_position == 'V'):
            if self.off_position == 'V':
                prim_assigned = 'SS'
            else:
                prim_assigned = 'NB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
                self.off_position == 'R' and '014t' in self.off_formation or
                self.off_position == 'R' and '113t' in self.off_formation or
                self.off_position == 'R' and '203' in self.off_formation or
                self.off_position == 'S'
                ):
                if self.off_position == 'R':
                    prim_assigned = 'NB' 
                else:
                    prim_assigned = 'DB'
        elif (self.off_position == 'Y' and '014t' in self.off_formation or 
            (self.off_position == 'T' and '023' in self.off_formation) or
            (self.off_position == 'T' and '122' in self.off_formation) or
            (self.off_position == 'T' and '131' in self.off_formation)
            ):
            if self.off_position == 'Y':
                prim_assigned = 'SS'
            elif self.off_position == 'T':
                if 'Regular' in self.def_formation:
                    prim_assigned = 'WLB'
                elif 'Nickel' in self.def_formation or 'Dime' in self.def_formation:
                    if '023' in self.off_formation:
                        prim_assigned = 'WLB'
                    else:
                        prim_assigned = 'NB'
            # todo: check to see if additional coverages are needed here
        elif ((self.off_position == 'Y' and '014 ' in self.off_formation) or
                (self.off_position == 'Y' and '113 ' in self.off_formation) or
                (self.off_position == 'Y' and '122' in self.off_formation) or
                (self.off_position == 'Y' and '221' in self.off_formation) or
                (self.off_position == 'Y' and '113t' in self.off_formation) or
                (self.off_position == 'Y' and '131' in self.off_formation) or
                (self.off_position == 'Y' and '212' in self.off_formation) or
                (self.off_position == 'Y' and '230' in self.off_formation) or
                (self.off_position == 'Y' and '023' in self.off_formation)
                ):
            prim_assigned = 'SS'
        elif self.off_position == 'RB':
            if '43' in self.def_formation:
                prim_assigned = 'MLB'
            else:
                if 'Weak' in self.def_formation:
                    prim_assigned = 'WILB'
                else:
                    prim_assigned = 'SILB'
        elif self.off_position == 'FB':
            prim_assigned = 'SLB'
        return prim_assigned, None

class Press2Assignment(CoverageAssignments):
    # sub class of coverage assignments for bump and run coverage
    def assign(self):
        prim_assigned = None
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):
            prim_assigned = 'LCB'
        elif (self.off_position == 'Z(FL)' or self.off_position == 'U'):
            prim_assigned = 'RCB'
        elif (self.off_position == 'R' and '014 ' in self.off_formation or
                self.off_position == 'R' and '023' in self.off_formation or
                self.off_position == 'R' and '113 ' in self.off_formation or
                self.off_position == 'V'
                ):
            if self.off_position == 'V':
                prim_assigned = None
            else:
                prim_assigned = 'NB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
                self.off_position == 'R' and '014t' in self.off_formation or
                self.off_position == 'R' and '113t' in self.off_formation or
                self.off_position == 'R' and '203' in self.off_formation or
                self.off_position == 'S'
                ):
                if self.off_position == 'R':
                    prim_assigned = 'NB' 
                else:
                    prim_assigned = 'DB'
        elif ((self.off_position == 'Y' and '014t' in self.off_formation) or 
            (self.off_position == 'T' and '023' in self.off_formation) or
            (self.off_position == 'T' and '122' in self.off_formation) or
            (self.off_position == 'T' and '131' in self.off_formation)
            ):
            if('Regular' in self.def_formation or 'Nickel' in self.def_formation):
                prim_assigned = 'WLB'
            else:   
                if ('43' in self.def_formation):
                    prim_assigned = 'MLB'
                elif ('34' in self.def_formation):
                    prim_assigned = 'WLB'
        elif ((self.off_position == 'Y' and '014 ' in self.off_formation) or
                (self.off_position == 'Y' and '113 ' in self.off_formation) or
                (self.off_position == 'Y' and '122' in self.off_formation) or
                (self.off_position == 'Y' and '221' in self.off_formation) or
                (self.off_position == 'Y' and '113t' in self.off_formation) or
                (self.off_position == 'Y' and '131' in self.off_formation) or
                (self.off_position == 'Y' and '212' in self.off_formation) or
                (self.off_position == 'Y' and '230' in self.off_formation) or
                (self.off_position == 'Y' and '023' in self.off_formation)
                ):
                    if('Regular' in self.def_formation or 'Nickel' in self.def_formation):
                        if ('43' in self.def_formation):
                            prim_assigned = 'SLB'
                        elif ('34' in self.def_formation):
                            prim_assigned = 'SILB'
                    else:
                        if '43' in self.def_formation:
                            prim_assigned = 'MLB'
                        else:
                            prim_assigned = 'SLB'
        elif self.off_position == 'RB':
            if '43' in self.def_formation:
                prim_assigned = 'MLB'
            else:
                if 'Weak' in self.off_formation:
                    prim_assigned = 'WILB'
                else:
                    prim_assigned = 'SILB'
        elif self.off_position == 'FB':
            prim_assigned = 'SLB'
        return prim_assigned, None
