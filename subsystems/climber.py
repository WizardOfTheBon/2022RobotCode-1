import wpilib
import ctre
import rev
import wpimath

class Climber:
    def __init__(self, config = dict):
        self.config = config
        self.leftShoulder = Shoulder(self.config["Climber"]["leftShoulder"]["ID"], self.config["Climber"]["leftShoulder"]["Name"])
        self.rightShoulder = Shoulder(self.config["Climber"]["rightShoulder"]["ID"], self.config["Climber"]["rightShoulder"]["Name"])
        self.leftWinch = Winch(self.config["Climber"]["leftWinch"]["ID"], self.config["Climber"]["leftWinch"]["Name"])
        self.rightWinch = Winch(self.config["Climber"]["rightWinch"]["ID"], self.config["Climber"]["rightWinch"]["Name"])
        
        self.leftHook = wpilib.Solenoid(self.config["Climber"]["leftHook_PCM_ID"])
        self.rightHook = wpilib.Solenoid(self.config["Climber"]["rightHook_PCM_ID"])

        self.shoulderPID = wpimath.controller.PIDcontroller(self.config["Climber"]["shoulderPID"]["kP"], self.config["Climber"]["shoulderPID"]["kI"], self.config["Climber"]["shoulderPID"]["kD"])
        self.winchPID = wpimath.controller.PIDcontroller(self.config["Climber"]["winchPID"]["kP"], self.config["Climber"]["winchPID"]["kI"], self.config["Climber"]["winchPID"]["kD"])

    def zeroEncoders(self):
        self.leftShoulder.encoder.setPosition(0)
        self.rightShoulder.encoder.setPosition(0)
        self.leftWinch.motor.setSelectedSensorPosition(0)
        self.rightWinch.motor.setSelectedSensorPosition(0)

    def setShoulderAngle(self, angle):
        self.shoulderPID.setSetpoint(angle)
        
        speed = self.shoulderPID.calculate(self.leftShoulder.getAngle())
        if speed > 0:
            self.leftShoulder.forward(speed)
        elif speed < 0:
            self.leftShoulder.backward(speed)
        else:
            self.leftShoulder.brake()
        
        speed = self.shoulderPID.calculate(self.rightShoulder.getAngle())
        if speed > 0:
            self.rightShoulder.forward(speed)
        elif speed < 0:
            self.rightShoulder.backward(speed)
        else:
            self.rightShoulder.brake()
    
    def moveShoulder(self, speed):
        if speed > 0:
            self.leftShoulder.forward(speed)
            self.rightShoulder.forward(speed)
        elif speed < 0:
            self.leftShoulder.backward(speed)
            self.rightShoulder.backward(speed)
        else:
            self.leftShoulder.brake()
            self.rightShoulder.brake()
    
    def setWinchPosition(self, position):
        self.winchPID.setSetpoint(position)
        
        speed = self.winchPID.calculate(self.leftWinch.getAngle())
        if speed > 0:
            self.leftWinch.forward(speed)
        elif speed < 0:
            self.leftWinch.backward(speed)
        else:
            self.leftWinch.brake()
        
        speed = self.winchPID.calculate(self.rightWinch.getAngle())
        if speed > 0:
            self.rightWinch.forward(speed)
        elif speed < 0:
            self.rightWinch.backward(speed)
        else:
            self.rightWinch.brake()
    
    def moveWinch(self, speed):
        if speed > 0:
            self.leftWinch.forward(speed)
            self.rightWinch.forward(speed)
        elif speed < 0:
            self.leftWinch.backward(speed)
            self.rightWinch.backward(speed)
        else:
            self.leftWinch.brake()
            self.rightWinch.brake()

    def extendArms(self):
        ''''''
    def firstBarGrab(self):
        ''''''
    def nextBarGrab(self):
        ''''''
    def pullArms(self):
        ''''''
    def detachArms(self):
        ''''''
    def engageHooks(self):
        ''''''
    def disengageHooks(self):
        ''''''

class Shoulder:
    '''The forward and backward directions need to be tested.'''
    def __init__(self, sparkID, name, config):
        self.motor = rev.CANSparkMax(sparkID, rev.MotorType.kBrushless)
        self.currentLimit = config["Climber"]["shoulderCurrentLimit"] # This amperage limit has not been tested
        self.velocityLimit = config["Climber"]["shoulderStressedVelocityThreshold"] # This number is for checking the current spike when motor stalls
        self.encoder = self.motor.getEncoder(counts_per_rev=2480)
        self.motor.FaultID.kSoftLimitRev = 0.01 # This is in rotations, and prevents backwards movement beyond the specified encoder value
        self.name = name
        if self.name == "leftShoulder":
            self.motor.setInverted(True)
        else:
            self.motor.setInverted(False)

    def forward(self, speed):
        self.motor.set(speed)
    
    def backward(self, speed):
        self.motor.set(speed)
        if self.motor.getFault(rev.CANSparkMax.FaultID.kSoftLimitRev):
            wpilib.SmartDashboard.putBool(self.name + " stopped", True)
        else:
            wpilib.SmartDashboard.putBool(self.name + " stopped", False)
    
    def getAngle(self):
        angle = self.encoder.getPosition() * 360
        return(angle)
    
    def brake(self):
        self.motor.set(0)
        self.motor.setIdleMode(rev.IdleMode.kBrake)

class Winch:
    '''The forward and backward directions need to be tested.'''
    def __init__(self, talonID, name, config):
        self.motor = ctre.TalonFX(talonID)
        self.currentLimit = config["Climber"]["winchCurrentLimit"] # This amperage limit has not been tested
        self.velocityLimit = config["Climber"]["winchStressedVelocityThreshold"] # This number is for checking the current spike when motor stalls
        self.motor.setSelectedSensorPosition(0)
        self.motor.configReverseSoftLimitThreshold(25) # This is in encoder ticks, and it prevents backwards movement beyond the specified encoder value
        self.name = name
        if self.name == "leftWinch":
            self.motor.setInverted(True)
        else:
            self.motor.setInverted(False)

    def release(self, speed):
        self.motor.set(ctre.ControlMode.PercentOutput, speed)

    def retract(self, speed):
        self.motor.set(ctre.ControlMode.PercentOutput, speed)
        if ctre.Faults.ReverseSoftLimit in self.motor.getFaults():
            wpilib.SmartDashboard.putBool(self.name + " stopped", False)
        else:
            wpilib.SmartDashboard.putBool(self.name + " stopped", True)
    
    def getPosition(self):
        position = self.motor.getSelectedSensorPosition()
        return(position)
    
    def brake(self):
        self.motor.set(ctre.ControlMode.PercentOutput, 0)
        self.motor.setNeutralMode(ctre.NeutralMode.Brake)
