class CoverageAssignments:
    def __init__(self, route, off_position, off_formation, def_formation):
        self.route = route
        self.off_position = off_position
        self.off_formation = off_formation
        self.def_formation = def_formation

    def assign(self):
        raise NotImplementedError("Subclasses should implement this method")
    
class ManCoverageAssignment(CoverageAssignments):
    # sub class of coverage assignments for man to man coverage
    def assign(self):
        if(self.off_position == 'X(SE)' or 
            (self.off_position == 'Z(FL)' and '131' in self.off_formation)
            or (self.off_position == 'T' and '221' in self.off_formation)
            or (self.off_position == 'T' and '230' in self.off_formation)):
            return 'LCB'
        elif (self.off_position == 'Z(FL)' or self.off_postion == 'U'):
            return 'RCB'
        elif (self.off_position == 'R' and '014' in self.off_formation or
            self.off_position == 'R' and '023' in self.off_formation or
            self.off_position == 'R' and '113' in self.off_formation or
            self.off_position == 'V'):
            if(self.off_position == 'V'):
                return 'SS'
            else:
                return 'NB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
            self.off_position == 'R' and '014t' in self.off_formation or
            self.off_position == 'R' and '113t' in self.off_formation or
            self.off_position == 'R' and '203' in self.off_formation or
            self.off_position == 'S'
            ):
            if self.off_position == 'R':
                return 'NB'
            else:
                return 'DB'
        elif ((self.off_position == 'Y' and '014t' in self.off_formation) or 
            (self.off_position == 'T' and '023' in self.off_formation) or
            (self.off_position == 'T' and '122' in self.off_formation) or
            (self.off_position == 'T' and '131' in self.off_formation)
            ):
            if self.off_position == 'Y':
                return 'SS'
            else:
                if 'Regular' in self.def_formation:
                    return 'WLB'
                elif 'Nickel' in self.def_formation or 'Dime' in self.def_formation:
                    if '023' in self.off_formation:
                        return 'WLB'
                    else:
                        return 'NB'
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
            return 'SS'
        elif self.off_position == 'RB':
            if '43' in self.def_formation:
                return 'MLB'
            else:
                if 'Weak' in self.def_formation:
                    return 'WILB'
                else:
                    return 'SILB' 
        elif self.off_position == 'FB':
            return 'SLB'
        else:
            raise ValueError('coverage assignment not found for route') 
            
        

class Tampa2CoverageAssignment(CoverageAssignments):
    # sub class of coverage assignments for tampa 2 coverage
    # todo: this logic needs to be updated to be route based instead of formation based
    def assign(self):
        if (self.position == 'X(SE)' or
            (self.position == 'Z(FL)' and '131' in self.off_formation) or
            (self.position == 'T' and '221' in self.off_formation) or
            (self.position == 'T' and '230' in self.off_formation)
            ):
            return 'LCB'
        elif (self.position == 'Z(FL)' or self.position == 'U'):
            if ('Man to Man' in self.def_formation or
                'Cover-2' in self.def_formation or
                'Cover-1' in self.def_formation or                            
                'Press-2' in self.def_formation or
                'Press-1' in self.def_formation or
                'Tampa-2' in self.def_formation
                ):
                return 'RCB'
        elif (self.off_position == 'R' and '014 ' in self.off_formation or
                self.off_position == 'R' and '023' in self.off_formation or
                self.off_position == 'R' and '113 ' in self.off_formation or
                self.off_position == 'V'
                ):
            if self.off_position == 'V':
                return 'None'
            else:
                return 'NB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
                self.off_position == 'R' and '014t' in self.off_formation or
                self.off_position == 'R' and '113t' in self.off_formation or
                self.off_position == 'R' and '203' in self.off_formation or
                self.off_position == 'S'
                ):
                if self.off_position == 'R':
                    return 'NB' 
                else:
                    return 'DB'
        elif ((self.off_position == 'Y' and '014t' in self.off_formation) or 
            (self.off_position == 'T' and '023' in self.off_formation) or
            (self.off_position == 'T' and '122' in self.off_formation) or
            (self.off_position == 'T' and '131' in self.off_formation)
            ):
            # todo: this logic needs to be fixed because in 43, WLB is not always on the field
            return 'WLB'
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
                            return 'SLB'
                        elif ('34' in self.def_formation):
                            return 'SILB'
                    else:
                        if '43' in self.def_formation:
                            return 'SLB'
                        else:
                            return 'SLB'
        elif self.off_position == 'RB':
            if '43' in self.def_formation:
                return ''
            else:
                if 'Weak' in self.off_formation:
                    return 'WILB'
                else:
                    return 'SILB'
        elif self.off_position == 'FB':
            # todo: this needs to account for nickel and dime
            return 'SLB'
        
        
        
        

class Cover1Assignment(CoverageAssignments):
    # sub class of coverage assignments for cover 1 coverage
    def assign(self):
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):
            return 'LCB'
        elif (self.off_position == 'Z(FL)' or self.off_position == 'U'):
            return 'RCB'
        elif (self.off_position == 'R' and '014' in self.off_formation or
            self.off_position == 'R' and '023' in self.off_formation or
            self.off_position == 'R' and '113' in self.off_formation or
            self.off_position == 'V'):
            if self.off_position == 'V':
                return 'SS'
            else:
                return 'NB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
                self.off_position == 'R' and '014t' in self.off_formation or
                self.off_position == 'R' and '113t' in self.off_formation or
                self.off_position == 'R' and '203' in self.off_formation or
                self.off_position == 'S'
                ):
                if self.off_position == 'R':
                    return 'NB' 
                else:
                    return 'DB'
        elif (self.off_position == 'Y' and '014t' in self.off_formation or 
            (self.off_position == 'T' and '023' in self.off_formation) or
            (self.off_position == 'T' and '122' in self.off_formation) or
            (self.off_position == 'T' and '131' in self.off_formation)
            ):
            if self.off_position == 'Y':
                return 'SS'
            elif self.off_position == 'T':
                if 'Regular' in self.def_formation:
                    return 'WLB'
                elif 'Nickel' in self.def_formation or 'Dime' in self.def_formation:
                    if '023' in self.off_formation:
                        return 'WLB'
                    else:
                        return 'NB'
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
            return 'SS'
        elif self.off_position == 'RB':
            if '43' in self.def_formation:
                return 'MLB'
            else:
                if 'Weak' in self.def_formation:
                    return 'WILB'
                else:
                    return 'SILB'
        elif self.off_position == 'FB':
            return 'SLB'
        # todo: need to check to see if only regular defense is on the field when fullback is on the field
        
        

class Cover2Assignment(CoverageAssignments):
    # sub class of coverage assignments for cover 2 coverage
    def assign(self):
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):
            return 'LCB'
        elif (self.off_position == 'Z(FL)' or self.off_position == 'U'):
            return 'RCB'
        elif (self.off_position == 'R' and '014 ' in self.off_formation or
                self.off_position == 'R' and '023' in self.off_formation or
                self.off_position == 'R' and '113 ' in self.off_formation or
                self.off_position == 'V'
                ):
            if self.off_position == 'V':
                return 'None'
            else:
                return 'NB'
        elif (self.off_position == 'R' and '005' in self.off_formation or
                self.off_position == 'R' and '014t' in self.off_formation or
                self.off_position == 'R' and '113t' in self.off_formation or
                self.off_position == 'R' and '203' in self.off_formation or
                self.off_position == 'S'
                ):
                if self.off_position == 'R':
                    return 'NB' 
                else:
                    return 'DB'
        elif ((self.off_position == 'Y' and '014t' in self.off_formation) or 
            (self.off_position == 'T' and '023' in self.off_formation) or
            (self.off_position == 'T' and '122' in self.off_formation) or
            (self.off_position == 'T' and '131' in self.off_formation)
            ):
            if('Regular' in self.def_formation or 'Nickel' in self.def_formation):
                return 'WLB'
            else:   
                if ('43' in self.def_formation):
                    return 'MLB'
                elif ('34' in self.def_formation):
                    return 'WLB'
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
                            return 'SLB'
                        elif ('34' in self.def_formation):
                            return 'SILB'
                    else:
                        if '43' in self.def_formation:
                            return 'MLB'
                        else:
                            return 'SLB'
        elif self.off_position == 'RB':
            if '43' in self.def_formation:
                return 'MLB'
            else:
                if 'Weak' in self.off_formation:
                    return 'WILB'
                else:
                    return 'SILB'
        elif self.off_position == 'FB':
            return 'SLB'
        

class Cover3Assignment(CoverageAssignments):
    # sub class of coverage assignments for cover 3 coverage
    def assign(self):
        if (self.off_position == 'X(SE)' or
            (self.off_position == 'Z(FL)' and '131' in self.off_formation) or
            (self.off_position == 'T' and '221' in self.off_formation) or
            (self.off_position == 'T' and '230' in self.off_formation)
            ):
            if('Cover-3 Cloud' in self.def_formation):
                match self.route:
                    case 'S Screen (S)':
                        if 'Regular' in self.def_formation:
                            return 'WLB'
                        else:
                            return 'LCB'
                    case 'Flat (0-4)':
                        if 'Regular' in self.def_formation:
                            return 'WLB'
                        else:
                            return 'LCB'
                    case '0 Dig (0-4)':
                        if ('43' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'MLB'                                        
                            elif('Nickel' in self.def_formation):
                                return 'WLB'                                        
                            else:
                                return 'MLB'                                    
                        elif ('34' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'WLB'                                        
                            elif('Nickel' in self.def_formation):
                                return 'WLB'                                        
                            else:
                                return 'WILB'
                    case '1 Out (5-8)':
                        if ('Regular' in self.def_formation):
                            return 'WLB'
                        else:
                            return 'LCB'
                    case '2 Slant (5-8)':
                        if ('43' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'MLB'                                        
                            elif('Nickel' in self.def_formation):
                                return 'WLB'                                        
                            else:
                                return 'MLB'                                    
                        elif ('34' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'WLB'                                        
                            elif('Nickel' in self.def_formation):
                                return 'WLB'                                        
                            else:
                                return 'WILB'
                    case '3 Comeback (9-12)':
                        if ('Regular' in self.def_formation):
                            return 'WLB'
                        else:
                            return 'LCB'
                    case '4 Curl (9-12)':
                        if ('43' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'MLB'
                            elif('Nickel' in self.def_formation):
                                return 'WLB'
                            else:
                                return 'MLB'
                        elif ('34' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'WLB'
                            elif('Nickel' in self.def_formation):
                                return 'WLB'
                            else:
                                return 'WILB'
                    case '5 Deep Out (13-18)':
                        if ('Regular' in self.def_formation):
                            return 'LCB'
                        else:
                            return 'NB'
                    case '6 Deep In (13-18)':
                        return 'FS'
                    case '7 Corner (19-26)':
                        if ('Regular' in self.def_formation):
                            return 'LCB'
                        else:
                            return 'NB'
                    case '8 Post (19-26)':
                        return 'FS'
                    case '9 Fade (27-39)':
                        if ('Regular' in self.def_formation):
                            return 'LCB'
                        else:
                            return 'NB'
                    case 'W Wheel (9-18)':
                        if ('Regular' in self.def_formation):
                            return 'LCB'
                        else:
                            return 'NB'
                    case 'D Deep Fade (40+)':
                        if ('Regular' in self.def_formation):
                            return 'LCB'
                        else:
                            return 'NB'
            elif ('Cover-3 Sky' in self.def_formation):
                match self.route:
                    case 'S Screen (S)':
                        if ('Regular' in self.def_formation):
                            return 'WLB'
                        else:
                            return 'LCB'
                    case 'F Flat (0-4)':
                        if ('Regular' in self.def_formation):
                            return 'WLB'
                        else:
                            return 'LCB'
                    case '0 Dig (0-4)':
                        if ('43' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'MLB'                                        
                            elif('Nickel' in self.def_formation):
                                return 'WLB'                                        
                            else:
                                return 'MLB'                                    
                        elif ('34' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'WLB'                                        
                            elif('Nickel' in self.def_formation):
                                return 'WLB'                                        
                            else:
                                return 'WILB'
                    case '1 Out (5-8)':
                        if ('Regular' in self.def_formation):
                            return 'WLB'
                        else:
                            return 'LCB'
                    case '2 Slant (5-8)':
                        if ('43' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'MLB'                                        
                            elif('Nickel' in self.def_formation):
                                return 'WLB'                                        
                            else:
                                return 'MLB'                                    
                        elif ('34' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'WLB'                                        
                            elif('Nickel' in self.def_formation):
                                return 'WLB'                                        
                            else:
                                return 'WILB'
                    case '3 Comeback (9-12)':
                        if ('Regular' in self.def_formation):
                            return 'WLB'                                    
                        else:
                            return 'LCB'
                    case '4 Curl (9-12)':
                        if ('43' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'MLB'                                        
                            elif('Nickel' in self.def_formation):
                                return 'WLB'                                        
                            else:
                                return 'MLB'
                        elif ('34' in self.def_formation):
                            if ('Dime' in self.def_formation):
                                return 'WLB'                                        
                            elif('Nickel' in self.def_formation):
                                return 'WLB'                                        
                            else:
                                return 'WILB'
                    case '5 Deep Out (13-18)':
                        if ('Regular' in self.def_formation):
                            return 'LCB'
                        else:
                            return 'NB'
                    case '6 Deep In (13-18)':
                        return 'FS'
                    case '7 Corner (19-26)':
                        if ('Regular' in self.def_formation):
                            return 'LCB'
                        else:
                            return 'NB'
                    case '8 Post (19-26)':
                        return 'FS'
                    case '9 Fade (27-39)':
                        if ('Regular' in self.def_formation):
                            return 'LCB'
                        else:
                            return 'NB'
                    case 'W Wheel (9-18)':
                        if ('Regular' in self.def_formation):
                            return 'LCB'
                        else:
                            return 'NB'
                    case 'D Deep Fade (40+)':
                        if ('Regular' in self.def_formation):
                            return 'LCB'
                        else:
                            return 'NB'       
                    

class Cover4Assignment(CoverageAssignments):
    # sub class of coverage assignments for cover 4 coverage
    def assign(self):
        pass

class Press1Assignment(CoverageAssignments):
    # sub class of coverage assignments for bump and run coverage
    def assign(self):
        pass

class Press2Assignment(CoverageAssignments):
    # sub class of coverage assignments for bump and run coverage
    def assign(self):
        pass