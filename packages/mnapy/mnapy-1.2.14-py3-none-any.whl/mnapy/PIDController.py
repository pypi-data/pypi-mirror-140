class PIDController:
    def __init__(self, set_point, k_p, k_i, k_d, context):
        self.context = context
        self.set_point = set_point
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.min_limit = -self.context.Params.SystemSettings.MAX_VOLTAGE
        self.max_limit = self.context.Params.SystemSettings.MAX_VOLTAGE
        self.previous_time = 0
        self.last_error = 0
        self.integral_error = 0

    def get_output(self, current_time: float, current_value: float) -> float:
        error: float = self.set_point - current_value
        dt: float = current_time - self.previous_time
        derivative_error: float = 0
        if dt != 0:
            derivative_error = (error - self.last_error) / dt
        else:
            derivative_error = 0

        self.integral_error += error * dt
        self.previous_time = current_time
        self.last_error = error
        return self.check_limits(
            self.k_p * error
            + self.k_i * self.integral_error
            + self.k_d * derivative_error
        )

    def reset(self) -> None:
        None
        self.previous_time = 0
        self.last_error = 0
        self.integral_error = 0

    def check_limits(self, output: float) -> float:
        None
        if output < self.min_limit:
            return self.min_limit
        elif output > self.max_limit:
            return self.max_limit
        else:
            return output

    def set_output_limits(self, min_limit: float, max_limit: float) -> None:
        None
        if min_limit < max_limit:
            self.min_limit = min_limit
            self.max_limit = max_limit
        else:
            self.min_limit = max_limit
            self.max_limit = min_limit

    def set_kp(self, k_p: float) -> None:
        None
        self.k_p = k_p
        self.reset()

    def set_ki(self, k_i: float) -> None:
        None
        self.k_i = k_i
        self.reset()

    def set_kd(self, k_d: float) -> None:
        None
        self.k_d = k_d
        self.reset()

    def set_setpoint(self, set_point: float) -> None:
        None
        self.reset()
        self.set_point = set_point
