from datetime import datetime, timedelta
from app.models import Driver, DrivingLog, Route
from app import db
import logging

logger = logging.getLogger(__name__)

class DOTComplianceManager:
    """Ensure compliance with DOT Hours of Service regulations"""
    
    # DOT HOS Rules (Property Carrying Drivers)
    MAX_DRIVING_HOURS = 11  # Maximum driving time
    MAX_ON_DUTY_HOURS = 14  # Maximum on-duty time
    REQUIRED_BREAK_MINUTES = 30  # Required break after 8 hours
    MIN_OFF_DUTY_HOURS = 10  # Minimum consecutive off-duty hours
    MAX_WEEKLY_HOURS = 60  # Maximum hours in 7 days
    MAX_BIWEEKLY_HOURS = 70  # Maximum hours in 8 days
    
    def validate_driver_assignment(self, driver_id, route):
        """Validate if driver can legally take this route"""
        driver = Driver.query.get(driver_id)
        if not driver:
            return False, "Driver not found"
        
        # Get driver's logs for compliance check
        driver_logs = self._get_driver_logs(driver_id, days=8)
        
        # Check daily driving hours
        today_driving = self._calculate_driving_hours_today(driver_logs)
        route_duration = route.estimated_duration_hours
        
        if today_driving + route_duration > self.MAX_DRIVING_HOURS:
            return False, f"Would exceed maximum daily driving hours ({self.MAX_DRIVING_HOURS}h)"
        
        # Check on-duty hours
        today_on_duty = self._calculate_on_duty_hours_today(driver_logs)
        if today_on_duty + route_duration > self.MAX_ON_DUTY_HOURS:
            return False, f"Would exceed maximum on-duty hours ({self.MAX_ON_DUTY_HOURS}h)"
        
        # Check if driver had required off-duty time
        last_shift_end = self._get_last_shift_end(driver_logs)
        if last_shift_end:
            off_duty_hours = (datetime.utcnow() - last_shift_end).total_seconds() / 3600
            if off_duty_hours < self.MIN_OFF_DUTY_HOURS:
                hours_needed = self.MIN_OFF_DUTY_HOURS - off_duty_hours
                return False, f"Insufficient off-duty time (need {hours_needed:.1f} more hours)"
        
        # Check weekly limits
        weekly_hours = self._calculate_weekly_hours(driver_logs)
        if weekly_hours + route_duration > self.MAX_WEEKLY_HOURS:
            return False, f"Would exceed weekly hour limit ({self.MAX_WEEKLY_HOURS}h in 7 days)"
        
        # Check 8-day limit
        eight_day_hours = self._calculate_eight_day_hours(driver_logs)
        if eight_day_hours + route_duration > self.MAX_BIWEEKLY_HOURS:
            return False, f"Would exceed 8-day hour limit ({self.MAX_BIWEEKLY_HOURS}h)"
        
        # Check break requirements
        continuous_driving = self._get_continuous_driving_time(driver_logs)
        if continuous_driving >= 8 and not self._has_recent_break(driver_logs):
            return False, "Required 30-minute break not taken after 8 hours"
        
        return True, "Assignment compliant with DOT HOS"
    
    def log_driving_time(self, driver_id, start_time, end_time, route_id, status='driving'):
        """Log driving time for HOS compliance"""
        log = DrivingLog(
            driver_id=driver_id,
            start_time=start_time,
            end_time=end_time,
            route_id=route_id,
            status=status,
            duration_hours=(end_time - start_time).total_seconds() / 3600
        )
        db.session.add(log)
        db.session.commit()
        
        # Auto-check for violations
        violations = self._check_hos_violations(driver_id)
        if violations:
            self._alert_violations(driver_id, violations)
        
        return log
    
    def get_driver_hos_status(self, driver_id):
        """Get current HOS status for driver"""
        logs = self._get_driver_logs(driver_id, days=8)
        
        today_driving = self._calculate_driving_hours_today(logs)
        today_on_duty = self._calculate_on_duty_hours_today(logs)
        weekly_hours = self._calculate_weekly_hours(logs)
        last_break = self._get_last_break_time(logs)
        
        # Calculate remaining hours
        remaining_driving = max(0, self.MAX_DRIVING_HOURS - today_driving)
        remaining_on_duty = max(0, self.MAX_ON_DUTY_HOURS - today_on_duty)
        remaining_weekly = max(0, self.MAX_WEEKLY_HOURS - weekly_hours)
        
        # Check if break is needed
        continuous_driving = self._get_continuous_driving_time(logs)
        break_needed = continuous_driving >= 8 and not self._has_recent_break(logs)
        
        return {
            'driver_id': driver_id,
            'current_status': {
                'driving_hours_today': round(today_driving, 2),
                'on_duty_hours_today': round(today_on_duty, 2),
                'weekly_hours': round(weekly_hours, 2),
                'last_break': last_break.isoformat() if last_break else None,
                'continuous_driving': round(continuous_driving, 2)
            },
            'remaining_hours': {
                'driving': round(remaining_driving, 2),
                'on_duty': round(remaining_on_duty, 2),
                'weekly': round(remaining_weekly, 2)
            },
            'compliance': {
                'break_needed': break_needed,
                'can_drive': remaining_driving > 0 and remaining_on_duty > 0,
                'violations': self._check_hos_violations(driver_id)
            }
        }
    
    def _get_driver_logs(self, driver_id, days):
        """Get driver logs for specified number of days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return DrivingLog.query.filter(
            DrivingLog.driver_id == driver_id,
            DrivingLog.start_time >= start_date
        ).order_by(DrivingLog.start_time).all()
    
    def _calculate_driving_hours_today(self, logs):
        """Calculate total driving hours today"""
        today = datetime.utcnow().date()
        total = 0
        
        for log in logs:
            if log.start_time.date() == today and log.status == 'driving':
                total += log.duration_hours
        
        return total
    
    def _calculate_on_duty_hours_today(self, logs):
        """Calculate total on-duty hours today"""
        today = datetime.utcnow().date()
        total = 0
        
        for log in logs:
            if log.start_time.date() == today and log.status in ['driving', 'on_duty']:
                total += log.duration_hours
        
        return total
    
    def _calculate_weekly_hours(self, logs):
        """Calculate total hours in last 7 days"""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        total = 0
        
        for log in logs:
            if log.start_time >= seven_days_ago and log.status in ['driving', 'on_duty']:
                total += log.duration_hours
        
        return total
    
    def _calculate_eight_day_hours(self, logs):
        """Calculate total hours in last 8 days"""
        eight_days_ago = datetime.utcnow() - timedelta(days=8)
        total = 0
        
        for log in logs:
            if log.start_time >= eight_days_ago and log.status in ['driving', 'on_duty']:
                total += log.duration_hours
        
        return total
    
    def _get_last_shift_end(self, logs):
        """Get end time of last shift"""
        for log in reversed(logs):
            if log.status in ['driving', 'on_duty']:
                return log.end_time
        return None
    
    def _get_continuous_driving_time(self, logs):
        """Calculate continuous driving time since last break"""
        continuous = 0
        last_break_time = None
        
        for log in reversed(logs):
            if log.status == 'break' and log.duration_hours >= 0.5:
                last_break_time = log.end_time
                break
            elif log.status == 'driving':
                if last_break_time and log.start_time > last_break_time:
                    break
                continuous += log.duration_hours
        
        return continuous
    
    def _has_recent_break(self, logs):
        """Check if driver has taken required break"""
        eight_hours_ago = datetime.utcnow() - timedelta(hours=8)
        
        for log in logs:
            if (log.status == 'break' and 
                log.duration_hours >= 0.5 and 
                log.start_time >= eight_hours_ago):
                return True
        
        return False
    
    def _get_last_break_time(self, logs):
        """Get time of last break"""
        for log in reversed(logs):
            if log.status == 'break' and log.duration_hours >= 0.5:
                return log.end_time
        return None
    
    def _check_hos_violations(self, driver_id):
        """Check for HOS violations"""
        violations = []
        logs = self._get_driver_logs(driver_id, days=8)
        
        # Check daily driving limit
        if self._calculate_driving_hours_today(logs) > self.MAX_DRIVING_HOURS:
            violations.append({
                'type': 'daily_driving_exceeded',
                'message': 'Exceeded 11-hour daily driving limit'
            })
        
        # Check on-duty limit
        if self._calculate_on_duty_hours_today(logs) > self.MAX_ON_DUTY_HOURS:
            violations.append({
                'type': 'daily_on_duty_exceeded',
                'message': 'Exceeded 14-hour on-duty limit'
            })
        
        # Check weekly limit
        if self._calculate_weekly_hours(logs) > self.MAX_WEEKLY_HOURS:
            violations.append({
                'type': 'weekly_hours_exceeded',
                'message': 'Exceeded 60-hour weekly limit'
            })
        
        # Check break requirement
        if self._get_continuous_driving_time(logs) >= 8 and not self._has_recent_break(logs):
            violations.append({
                'type': 'break_required',
                'message': '30-minute break required after 8 hours'
            })
        
        return violations
    
    def _alert_violations(self, driver_id, violations):
        """Alert about HOS violations"""
        for violation in violations:
            logger.warning(f"HOS Violation for driver {driver_id}: {violation['message']}")
            
            # Create violation record
            from app.models import HOSViolation
            violation_record = HOSViolation(
                driver_id=driver_id,
                violation_type=violation['type'],
                description=violation['message'],
                timestamp=datetime.utcnow()
            )
            db.session.add(violation_record)
        
        db.session.commit()
