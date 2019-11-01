#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

t = 0
q = [1, 0, 0, 0]
eInt = [0, 0, 0]

# # version C de Madgwick 2012
# def madgwick_Q6_Update(ax, ay, az, gx, gy, gz, new_time):
#     global t, q
#
#     Beta = 0.1
#     q1, q2, q3, q4 = q[0], q[1], q[2], q[3] # short name local variable for readability
#
#     delta_t = (new_time - t) * 0.001
#     t = new_time

# version matlab de Madgwick 2012-2013
def madgwick_Q6_Update(ax, ay, az, gx, gy, gz, new_time):
    global t, q

    Beta = 0.1
    q1, q2, q3, q4 = q[0], q[1], q[2], q[3] # short name local variable for readability

    delta_t = (new_time - t) * 0.001
    t = new_time

    # Auxiliary variables to avoid repeated arithmetic
    _2q1 = 2 * q1
    _2q2 = 2 * q2
    _2q3 = 2 * q3
    _2q4 = 2 * q4
    _4q1 = 4 * q1
    _4q2 = 4 * q2
    _4q3 = 4 * q3
    _8q2 = 8 * q2
    _8q3 = 8 * q3
    q1q1 = q1 * q1
    q2q2 = q2 * q2
    q3q3 = q3 * q3
    q4q4 = q4 * q4

    # Normalise accelerometer measurement
    norm = math.sqrt(ax * ax + ay * ay + az * az)
    if (norm == 0):
        return None
    else:
        norm = 1 / norm # use reciprocal for division
        ax = ax * norm
        ay = ay * norm
        az = az * norm

    # Gradient decent algorithm corrective step
    s1 = _4q1 * q3q3 + _2q3 * ax + _4q1 * q2q2 - _2q2 * ay
    s2 = _4q2 * q4q4 - _2q4 * ax + 4 * q1q1 * q2 - _2q1 * ay - _4q2 + _8q2 * q2q2 + _8q2 * q3q3 + _4q2 * az
    s3 = 4 * q1q1 * q3 + _2q1 * ax + _4q3 * q4q4 - _2q4 * ay - _4q3 + _8q3 * q2q2 + _8q3 * q3q3 + _4q3 * az
    s4 = 4 * q2q2 * q4 - _2q2 * ax + 4 * q3q3 * q4 - _2q3 * ay
    norm = 1 / math.sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4) # normalise step magnitude
    s1 = s1 * norm
    s2 = s2 * norm
    s3 = s3 * norm
    s4 = s4 * norm

    # Compute rate of change of quaternion
    qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - Beta * s1
    qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - Beta * s2
    qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - Beta * s3
    qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - Beta * s4

    # Integrate to yield quaternion
    q1 = q1 + qDot1 * delta_t
    q2 = q2 + qDot2 * delta_t
    q3 = q3 + qDot3 * delta_t
    q4 = q4 + qDot4 * delta_t
    norm = 1 / math.sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4) # normalise quaternion
    q[0] = q1 * norm
    q[1] = q2 * norm
    q[2] = q3 * norm
    q[3] = q4 * norm

    return [q[0], q[1], q[2], q[3]]

# version matlab de Madgwick 2012-2013
def mahony_Q6_Update(ax, ay, az, gx, gy, gz, new_time):
    global t, q

    Kp = 2 * 5
    Ki = 0

    q1, q2, q3, q4 = q[0], q[1], q[2], q[3] # short name local variable for readability

    delta_t = (new_time - t) * 0.001
    t = new_time

    # Normalise accelerometer measurement
    norm = math.sqrt(ax * ax + ay * ay + az * az)
    if (norm == 0):
        return None
    else:
        norm = 1 / norm # use reciprocal for division
        ax = ax * norm
        ay = ay * norm
        az = az * norm

    # Estimated direction of gravity
    vx = 2 * (q2 * q4 - q1 * q3)
    vy = 2 * (q1 * q2 + q3 * q4)
    vz = q1 * q1 - q2 * q2 - q3 * q3 + q4 * q4

    # Error is cross product between estimated direction and measured direction of gravity
    ex = (ay * vz - az * vy)
    ey = (az * vx - ax * vz)
    ez = (ax * vy - ay * vx)
    if (Ki > 0):
        eInt[0] = eInt[0] + ex # accumulate integral error
        eInt[1] = eInt[1] + ey
        eInt[2] = eInt[2] + ez
    else:
        eInt[0] = 0 # prevent integral wind up
        eInt[1] = 0
        eInt[2] = 0

    # Apply feedback terms
    gx = gx + Kp * ex + Ki * eInt[0]
    gy = gy + Kp * ey + Ki * eInt[1]
    gz = gz + Kp * ez + Ki * eInt[2]

    # Integrate rate of change of quaternion
    pa = q2
    pb = q3
    pc = q4
    q1 = q1 + (-q2 * gx - q3 * gy - q4 * gz) * (0.5 * delta_t)
    q2 = pa + (q1 * gx + pb * gz - pc * gy) * (0.5 * delta_t)
    q3 = pb + (q1 * gy - pa * gz + pc * gx) * (0.5 * delta_t)
    q4 = pc + (q1 * gz + pa * gy - pb * gx) * (0.5 * delta_t)

    norm = 1 / math.sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4) # normalise quaternion
    q[0] = q1 * norm
    q[1] = q2 * norm
    q[2] = q3 * norm
    q[3] = q4 * norm

    return [q[0], q[1], q[2], q[3]]

def original_madgwick_Q6_Update(ax, ay, az, gx, gy, gz, new_time):
    global t, q

    GyroMeasError = math.pi * (40 / 180)
    GyroMeasDrift = math.pi * (0  / 180) # gyroscope measurement drift in rad/s/s (start at 0.0 deg/s/s)
    # There is a tradeoff in the beta parameter between accuracy and response
    # speed. In the original Madgwick study, beta of 0.041 (corresponding to
    # GyroMeasError of 2.7 degrees/s) was found to give optimal accuracy.
    # However, with this value, the LSM9SD0 response time is about 10 seconds
    # to a stable initial quaternion. Subsequent changes also require a
    # longish lag time to a stable output, not fast enough for a quadcopter or
    # robot car! By increasing beta (GyroMeasError) by about a factor of
    # fifteen, the response time constant is reduced to ~2 sec. I haven't
    # noticed any reduction in solution accuracy. This is essentially the I
    # coefficient in a PID control sense; the bigger the feedback coefficient,
    # the faster the solution converges, usually at the expense of accuracy.
    # In any case, this is the free parameter in the Madgwick filtering and
    # fusion scheme.
    beta = math.sqrt(3 / 4) * GyroMeasError # Compute beta

    delta_t = (new_time - t) * 0.001
    t = new_time

    # Local system variables

    SEq_1, SEq_2, SEq_3, SEq_4 = q[0], q[1], q[2], q[3] # estimated orientation quaternion elements

    # Auxilirary variables to avoid reapeated calcualtions
    halfSEq_1 = 0.5 * SEq_1
    halfSEq_2 = 0.5 * SEq_2
    halfSEq_3 = 0.5 * SEq_3
    halfSEq_4 = 0.5 * SEq_4
    twoSEq_1 = 2 * SEq_1
    twoSEq_2 = 2 * SEq_2
    twoSEq_3 = 2 * SEq_3
    # Normalise the accelerometer measurement
    norm = math.sqrt(ax * ax + ay * ay + az * az)
    ax = ax / norm
    ay = ay / norm
    az = az / norm
    # Compute the objective function and Jacobian
    f_1 = twoSEq_2 * SEq_4 - twoSEq_1 * SEq_3 - ax
    f_2 = twoSEq_1 * SEq_2 + twoSEq_3 * SEq_4 - ay
    f_3 = 1 - twoSEq_2 * SEq_2 - twoSEq_3 * SEq_3 - az
    J_11or24 = twoSEq_3 # J_11 negated in matrix multiplication
    J_12or23 = 2 * SEq_4
    J_13or22 = twoSEq_1 # J_12 negated in matrix multiplication
    J_14or21 = twoSEq_2
    J_32 = 2 * J_14or21 # negated in matrix multiplication
    J_33 = 2 * J_11or24 # negated in matrix multiplication
    # Compute the gradient (matrix multiplication)
    SEqHatDot_1 = J_14or21 * f_2 - J_11or24 * f_1
    SEqHatDot_2 = J_12or23 * f_1 + J_13or22 * f_2 - J_32 * f_3
    SEqHatDot_3 = J_12or23 * f_2 - J_33 * f_3 - J_13or22 * f_1
    SEqHatDot_4 = J_14or21 * f_1 + J_11or24 * f_2
    # Normalise the gradient
    norm = math.sqrt(SEqHatDot_1 * SEqHatDot_1 + SEqHatDot_2 * SEqHatDot_2 + SEqHatDot_3 * SEqHatDot_3 + SEqHatDot_4 * SEqHatDot_4)
    SEqHatDot_1 = SEqHatDot_1 / norm
    SEqHatDot_2 = SEqHatDot_2 / norm
    SEqHatDot_3 = SEqHatDot_3 / norm
    SEqHatDot_4 = SEqHatDot_4 / norm
    # Compute the quaternion derrivative measured by gyroscopes
    SEqDot_omega_1 = -halfSEq_2 * gx - halfSEq_3 * gy - halfSEq_4 * gz
    SEqDot_omega_2 = halfSEq_1 * gx + halfSEq_3 * gz - halfSEq_4 * gy
    SEqDot_omega_3 = halfSEq_1 * gy - halfSEq_2 * gz + halfSEq_4 * gx
    SEqDot_omega_4 = halfSEq_1 * gz + halfSEq_2 * gy - halfSEq_3 * gx
    # Compute then integrate the estimated quaternion derrivative
    SEq_1 = SEq_1 + (SEqDot_omega_1 - (beta * SEqHatDot_1)) * delta_t
    SEq_2 = SEq_2 + (SEqDot_omega_2 - (beta * SEqHatDot_2)) * delta_t
    SEq_3 = SEq_3 + (SEqDot_omega_3 - (beta * SEqHatDot_3)) * delta_t
    SEq_4 = SEq_4 + (SEqDot_omega_4 - (beta * SEqHatDot_4)) * delta_t
    # Normalise quaternion
    norm = math.sqrt(SEq_1 * SEq_1 + SEq_2 * SEq_2 + SEq_3 * SEq_3 + SEq_4 * SEq_4)
    SEq_1 = SEq_1 / norm
    SEq_2 = SEq_2 / norm
    SEq_3 = SEq_3 / norm
    SEq_4 = SEq_4 / norm
    q[0] = SEq_1
    q[1] = SEq_2
    q[2] = SEq_3
    q[3] = SEq_4

    return q[0], q[1], q[2], q[3]

def madgwickUpdate(ax, ay, az, gx, gy, gz, mx, my, mz, new_time):
    global t, q
    GyroMeasError = math.pi * (40 / 180)
    GyroMeasDrift = math.pi * (0  / 180) # gyroscope measurement drift in rad/s/s (start at 0.0 deg/s/s)
    # There is a tradeoff in the beta parameter between accuracy and response
    # speed. In the original Madgwick study, beta of 0.041 (corresponding to
    # GyroMeasError of 2.7 degrees/s) was found to give optimal accuracy.
    # However, with this value, the LSM9SD0 response time is about 10 seconds
    # to a stable initial quaternion. Subsequent changes also require a
    # longish lag time to a stable output, not fast enough for a quadcopter or
    # robot car! By increasing beta (GyroMeasError) by about a factor of
    # fifteen, the response time constant is reduced to ~2 sec. I haven't
    # noticed any reduction in solution accuracy. This is essentially the I
    # coefficient in a PID control sense; the bigger the feedback coefficient,
    # the faster the solution converges, usually at the expense of accuracy.
    # In any case, this is the free parameter in the Madgwick filtering and
    # fusion scheme.
    beta = math.sqrt(3 / 4) * GyroMeasError # Compute beta
    zeta = math.sqrt(3 / 4) * GyroMeasDrift # Compute zeta, the other free parameter in the Madgwick scheme usually set to a small or zero value

    delta_t = (new_time - t) * 0.001
    t = new_time
    q1, q2, q3, q4 = q[0], q[1], q[2], q[3]

    # Auxiliary variables to avoid repeated arithmetic
    _2q1 = 2 * q1
    _2q1 = 2 * q1
    _2q1 = 2 * q1
    _2q2 = 2 * q2
    _2q2 = 2 * q2
    _2q2 = 2 * q2
    _2q3 = 2 * q3
    _2q3 = 2 * q3
    _2q3 = 2 * q3
    _2q4 = 2 * q4
    _2q4 = 2 * q4
    _2q4 = 2 * q4
    _2q1q3 = 2 * q1 * q3
    _2q1q3 = 2 * q1 * q3
    _2q1q3 = 2 * q1 * q3
    _2q3q4 = 2 * q3 * q4
    _2q3q4 = 2 * q3 * q4
    _2q3q4 = 2 * q3 * q4
    q1q1 = q1 * q1
    q1q2 = q1 * q2
    q1q2 = q1 * q2
    q1q3 = q1 * q3
    q1q4 = q1 * q4
    q2q2 = q2 * q2
    q2q3 = q2 * q3
    q2q4 = q2 * q4
    q3q3 = q3 * q3
    q3q4 = q3 * q4
    q4q4 = q4 * q4

    # Normalise accelerometer measurement
    norm = 1 / math.sqrt(ax * ax + ay * ay + az * az)
    ax = ax * norm
    ay = ay * norm
    az = az * norm
    # Normalise magnetometer measurement
    norm = 1 / math.sqrt(mx * mx + my * my + mz * mz)
    mx = mx * norm
    my = my * norm
    mz = mz * norm

    # Reference direction of Earth's magnetic field
    _2q1mx = 2 * q1 * mx
    _2q1my = 2 * q1 * my
    _2q1mz = 2 * q1 * mz
    _2q2mx = 2 * q2 * mx
    hx = mx * q1q1 - _2q1my * q4 + _2q1mz * q3 + mx * q2q2 + _2q2 * my * q3 + _2q2 * mz * q4 - mx * q3q3 - mx * q4q4
    hy = _2q1mx * q4 + my * q1q1 - _2q1mz * q2 + _2q2mx * q3 - my * q2q2 + my * q3q3 + _2q3 * mz * q4 - my * q4q4
    _2bx = math.sqrt(hx * hx + hy * hy)
    _2bz = -_2q1mx * q3 + _2q1my * q2 + mz * q1q1 + _2q2mx * q4 - mz * q2q2 + _2q3 * my * q4 - mz * q3q3 + mz * q4q4
    _4bx = 2 * _2bx
    _4bz = 2 * _2bz

    # Gradient decent algorithm corrective step
    s1 = -_2q3 * (2 * q2q4 - _2q1q3 - ax) + _2q2 * (2 * q1q2 + _2q3q4 - ay) - _2bz * q3 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q4 + _2bz * q2) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + _2bx * q3 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    s1 = -_2q3 * (2 * q2q4 - _2q1q3 - ax) + _2q2 * (2 * q1q2 + _2q3q4 - ay) - _2bz * q3 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q4 + _2bz * q2) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + _2bx * q3 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    s2 = _2q4 * (2 * q2q4 - _2q1q3 - ax) + _2q1 * (2 * q1q2 + _2q3q4 - ay) - 4 * q2 * (1 - 2 * q2q2 - 2 * q3q3 - az) + _2bz * q4 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q3 + _2bz * q1) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + (_2bx * q4 - _4bz * q2) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    s2 = _2q4 * (2 * q2q4 - _2q1q3 - ax) + _2q1 * (2 * q1q2 + _2q3q4 - ay) - 4 * q2 * (1 - 2 * q2q2 - 2 * q3q3 - az) + _2bz * q4 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q3 + _2bz * q1) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + (_2bx * q4 - _4bz * q2) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    s3 = -_2q1 * (2 * q2q4 - _2q1q3 - ax) + _2q4 * (2 * q1q2 + _2q3q4 - ay) - 4 * q3 * (1 - 2 * q2q2 - 2 * q3q3 - az) + (-_4bx * q3 - _2bz * q1) * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q2 + _2bz * q4) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + (_2bx * q1 - _4bz * q3) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    s3 = -_2q1 * (2 * q2q4 - _2q1q3 - ax) + _2q4 * (2 * q1q2 + _2q3q4 - ay) - 4 * q3 * (1 - 2 * q2q2 - 2 * q3q3 - az) + (-_4bx * q3 - _2bz * q1) * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q2 + _2bz * q4) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + (_2bx * q1 - _4bz * q3) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    s4 = _2q2 * (2 * q2q4 - _2q1q3 - ax) + _2q3 * (2 * q1q2 + _2q3q4 - ay) + (-_4bx * q4 + _2bz * q2) * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q1 + _2bz * q3) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + _2bx * q2 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    s4 = _2q2 * (2 * q2q4 - _2q1q3 - ax) + _2q3 * (2 * q1q2 + _2q3q4 - ay) + (-_4bx * q4 + _2bz * q2) * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q1 + _2bz * q3) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + _2bx * q2 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    norm = 1 / math.sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4) # normalise step magnitude
    s1 = s1 * norm
    s2 = s2 * norm
    s3 = s3 * norm
    s4 = s4 * norm

    # Compute rate of change of quaternion
    qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - beta * s1
    qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - beta * s2
    qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - beta * s3
    qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - beta * s4

    # Integrate to yield quaternion
    q1 = q1 + qDot1 * delta_t
    q2 = q2 + qDot2 * delta_t
    q3 = q3 + qDot3 * delta_t
    q4 = q4 + qDot4 * delta_t
    norm = 1 / math.sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4) # normalise quaternion
    q[0] = q1 * norm
    q[1] = q2 * norm
    q[2] = q3 * norm
    q[3] = q4 * norm

    return q[0], q[1], q[2], q[3]

# # Similar to Madgwick scheme but uses proportional and integral filtering on
# # the error between estimated reference vectors and measured ones.
# def mahonyQuaternionUpdate(data, last_q, delta_t): # delta_t unit is second
#     # Sensors x (y)-axis of the accelerometer is aligned with the y (x)-axis of
#     # the magnetometer; the magnetometer z-axis (+ down) is opposite to z-axis
#     # (+ up) of accelerometer and gyro! We have to make some allowance for this
#     # orientationmismatch in feeding the output to the quaternion filter. For the
#     # MPU-9250, we have chosen a magnetic rotation that keeps the sensor forward
#     # along the x-axis just like in the LSM9DS0 sensor. This rotation can be
#     # modified to allow any convenient orientation convention. This is ok by
#     # aircraft orientation standards! Pass gyro rate as rad/s
#
#     Kp = 2 * 5 # These are the free parameters in the Mahony filter and fusion scheme, Kp for proportional feedback
#     Ki = 0 # Ki for integral
#     eInt = [0, 0, 0] # Vector to hold integral error for Mahony method
#
#     ax, ay, az = data[1], data[2], data[3] # short name local variable for readability
#     gx, gy, gz = data[4] * math.pi / 180, data[5] * math.pi / 180, data[6] * math.pi / 180
#     my, mx, mz = data[7], data[8], data[9]
#     q1, q2, q3, q4 = last_q[0], last_q[1], last_q[2], last_q[3]
#
#     # Auxiliary variables to avoid repeated arithmetic
#     q1q1 = q1 * q1
#     q1q2 = q1 * q2
#     q1q3 = q1 * q3
#     q1q4 = q1 * q4
#     q2q2 = q2 * q2
#     q2q3 = q2 * q3
#     q2q4 = q2 * q4
#     q3q3 = q3 * q3
#     q3q4 = q3 * q4
#     q4q4 = q4 * q4
#
#     # Normalise accelerometer measurement
#     norm = 1 / math.sqrt(ax * ax + ay * ay + az * az)
#     ax = ax * norm
#     ay = ay * norm
#     az = az * norm
#     # Normalise magnetometer measurement
#     norm = 1 / math.sqrt(mx * mx + my * my + mz * mz)
#     mx = mx * norm
#     my = my * norm
#     mz = mz * norm
#     # Reference direction of Earth’s magnetic field
#     hx = 2 * mx * (0.5 - q3q3 - q4q4) + 2 * my * (q2q3 - q1q4) + 2 * mz * (q2q4 + q1q3)
#     hy = 2 * mx * (q2q3 + q1q4) + 2 * my * (0.5 - q2q2 - q4q4) + 2 * mz * (q3q4 - q1q2)
#     bx = math.sqrt((hx * hx) + (hy * hy))
#     bz = 2 * mx * (q2q4 - q1q3) + 2 * my * (q3q4 + q1q2) + 2 * mz * (0.5 - q2q2 - q3q3)
#     # Estimated direction of gravity and magnetic field
#     vx = 2 * (q2q4 - q1q3)
#     vy = 2 * (q1q2 + q3q4)
#     vz = q1q1 - q2q2 - q3q3 + q4q4
#     wx = 2 * bx * (0.5 - q3q3 - q4q4) + 2 * bz * (q2q4 - q1q3)
#     wy = 2 * bx * (q2q3 - q1q4) + 2 * bz * (q1q2 + q3q4)
#     wz = 2 * bx * (q1q3 + q2q4) + 2 * bz * (0.5 - q2q2 - q3q3)
#     # Error is cross product between estimated direction and measured direction of gravity
#     ex = (ay * vz - az * vy) + (my * wz - mz * wy)
#     ey = (az * vx - ax * vz) + (mz * wx - mx * wz)
#     ez = (ax * vy - ay * vx) + (mx * wy - my * wx)
#     if (Ki > 0):
#         eInt[0] = eInt[0] + ex # accumulate integral error
#         eInt[1] = eInt[1] + ey
#         eInt[2] = eInt[2] + ez
#     else:
#         eInt[0] = 0 # prevent integral wind up
#         eInt[1] = 0
#         eInt[2] = 0
#     # Apply feedback terms
#     gx = gx + Kp * ex + Ki * eInt[0]
#     gy = gy + Kp * ey + Ki * eInt[1]
#     gz = gz + Kp * ez + Ki * eInt[2]
#     # Integrate rate of change of quaternion
#     pa = q2
#     pb = q3
#     pc = q4
#     q1 = q1 + (-q2 * gx - q3 * gy - q4 * gz) * (0.5 * delta_t)
#     q2 = pa + (q1 * gx + pb * gz - pc * gy) * (0.5 * delta_t)
#     q3 = pb + (q1 * gy - pa * gz + pc * gx) * (0.5 * delta_t)
#     q4 = pc + (q1 * gz + pa * gy - pb * gx) * (0.5 * delta_t)
#     # Normalise quaternion
#     norm = 1 / math.sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4)
#     q1 = q1 * norm
#     q2 = q2 * norm
#     q3 = q3 * norm
#     q4 = q4 * norm
#
#     return q1, q2, q3, q4
#
# def original_madgwickQuaternionUpdate(data, last_q, last_t, last_b, last_w_b):
#     # System constants
#     gyroMeasError = 3.14159265358979 * (5 / 180) # gyroscope measurement error in rad/s (shown as 5 deg/s)
#     gyroMeasDrift = 3.14159265358979 * (0.2 / 180) # gyroscope measurement error in rad/s/s (shown as 0.2f deg/s/s)
#     beta = math.sqrt(3 / 4) * gyroMeasError # compute beta
#     zeta = math.sqrt(3 / 4) * gyroMeasDrift # compute zeta
#
#     # Global system variables
#     t = data[0]
#     delta_t = (t - last_t) * 0.001 # sampling period in seconds (shown as 1 ms)
#     print(delta_t)
#     a_x, a_y, a_z = data[1], data[2], data[3] # accelerometer measurements
#     w_x, w_y, w_z = data[4] * math.pi / 180, data[5] * math.pi / 180, data[6] * math.pi / 180 # gyroscope measurements in rad/s
#     m_y, m_x, m_z = data[7], data[8], data[9] # magnetometer measurements
#     SEq_1, SEq_2, SEq_3, SEq_4 = last_q[0], last_q[1], last_q[2], last_q[3] # estimated orientation quaternion elements
#     b_x, b_z = last_b[0], last_b[1] # reference direction of flux in earth frame
#     w_bx, w_by, w_bz = last_w_b[0], last_w_b[1], last_w_b[2] #  estimate gyroscope biases error
#
#     # local system variables
# # float norm; // vector norm
# # float SEqDot_omega_1, SEqDot_omega_2, SEqDot_omega_3, SEqDot_omega_4; // quaternion rate from gyroscopes elements
# # float f_1, f_2, f_3, f_4, f_5, f_6; // objective function elements
# # float J_11or24, J_12or23, J_13or22, J_14or21, J_32, J_33, // objective function Jacobian elements
# # J_41, J_42, J_43, J_44, J_51, J_52, J_53, J_54, J_61, J_62, J_63, J_64; //
# # float SEqHatDot_1, SEqHatDot_2, SEqHatDot_3, SEqHatDot_4; // estimated direction of the gyroscope error
# # float w_err_x, w_err_y, w_err_z; // estimated direction of the gyroscope error (angular)
# # float h_x, h_y, h_z; // computed flux in the earth frame
#
#     # axulirary variables to avoid reapeated calcualtions
#     halfSEq_1 = 0.5 * SEq_1
#     halfSEq_2 = 0.5 * SEq_2
#     halfSEq_3 = 0.5 * SEq_3
#     halfSEq_4 = 0.5 * SEq_4
#     twoSEq_1 = 2 * SEq_1
#     twoSEq_2 = 2 * SEq_2
#     twoSEq_3 = 2 * SEq_3
#     twoSEq_4 = 2 * SEq_4
#     twob_x = 2 * iuin,;;;;;;;;;;;;;;;;; b_x
#     twob_z = 2 * b_z
#     twob_xSEq_1 = 2 * b_x * SEq_1
#     twob_xSEq_2 = 2 * b_x * SEq_2
#     twob_xSEq_3 = 2 * b_x * SEq_3,
#     twob_xSEq_4 = 2 * b_x * SEq_4
#     twob_zSEq_1 = 2 * b_z * SEq_1
#     twob_zSEq_2 = 2 * b_z * SEq_2
#     twob_zSEq_3 = 2 * b_z * SEq_3
#     twob_zSEq_4 = 2 * b_z * SEq_4
#     # SEq_1SEq_2
#     SEq_1SEq_3 = SEq_1 * SEq_3
#     # SEq_1SEq_4
#     # SEq_2SEq_3
#     SEq_2SEq_4 = SEq_2 * SEq_4
#     # SEq_3SEq_4
#     twom_x = 2 * m_x
#     twom_y = 2 * m_y
#     twom_z = 2 * m_z
#
#     # normalise the accelerometer measurement
#     norm = 1 / math.sqrt(a_x * a_x + a_y * a_y + a_z * a_z)
#     a_x = a_x * norm
#     a_y = a_y * norm
#     a_z = a_z * norm
#     # normalise the magnetometer measurement
#     norm = 1 / math.sqrt(m_x * m_x + m_y * m_y + m_z * m_z)
#     m_x = m_x * norm
#     m_y = m_y * norm
#     m_z = m_z * norm/
#
#     # compute the objective function and Jacobian
#     f_1 = twoSEq_2 * SEq_4 - twoSEq_1 * SEq_3 - a_x
#     f_2 = twoSEq_1 * SEq_2 + twoSEq_3 * SEq_4 - a_y
#     f_3 = 1 - twoSEq_2 * SEq_2 - twoSEq_3 * SEq_3 - a_z
#     f_4 = twob_x * (0.5 - SEq_3 * SEq_3 - SEq_4 * SEq_4) + twob_z * (SEq_2SEq_4 - SEq_1SEq_3) - m_x
#     f_5 = twob_x * (SEq_2 * SEq_3 - SEq_1 * SEq_4) + twob_z * (SEq_1 * SEq_2 + SEq_3 * SEq_4) - m_y
#     f_6 = twob_x * (SEq_1SEq_3 + SEq_2SEq_4) + twob_z * (0.5 - SEq_2 * SEq_2 - SEq_3 * SEq_3) - m_z
#     J_11or24 = twoSEq_3 # J_11 negated in matrix multiplication
#     J_12or23 = 2 * SEq_4
#     J_13or22 = twoSEq_1 # J_12 negated in matrix multiplication
#     J_14or21 = twoSEq_2
#     J_32 = 2 * J_14or21 # negated in matrix multiplication
#     J_33 = 2 * J_11or24 # negated in matrix multiplication
#     J_41 = twob_zSEq_3 # negated in matrix multiplication
#     J_42 = twob_zSEq_4
#     J_43 = 2 * twob_xSEq_3 + twob_zSEq_1 # negated in matrix multiplication
#     J_44 = 2 * twob_xSEq_4 - twob_zSEq_2 # negated in matrix multiplication
#     J_51 = twob_xSEq_4 - twob_zSEq_2 # negated in matrix multiplication
#     J_52 = twob_xSEq_3 + twob_zSEq_1
#     J_53 = twob_xSEq_2 + twob_zSEq_4
#     J_54 = twob_xSEq_1 - twob_zSEq_3 # negated in matrix multiplication
#     J_61 = twob_xSEq_3
#     J_62 = twob_xSEq_4 - 2 * twob_zSEq_2
#     J_63 = twob_xSEq_1 - 2 * twob_zSEq_3
#     J_64 = twob_xSEq_2
#
#     # compute the gradient (matrix multiplication)
#     SEqHatDot_1 = J_14or21 * f_2 - J_11or24 * f_1 - J_41 * f_4 - J_51 * f_5 + J_61 * f_6
#     SEqHatDot_2 = J_12or23 * f_1 + J_13or22 * f_2 - J_32 * f_3 + J_42 * f_4 + J_52 * f_5 + J_62 * f_6
#     SEqHatDot_3 = J_12or23 * f_2 - J_33 * f_3 - J_13or22 * f_1 - J_43 * f_4 + J_53 * f_5 + J_63 * f_6
#     SEqHatDot_4 = J_14or21 * f_1 + J_11or24 * f_2 - J_44 * f_4 - J_54 * f_5 + J_64 * f_6
#
#     # normalise the gradient to estimate direction of the gyroscope error
#     norm = 1 / math.sqrt(SEqHatDot_1 * SEqHatDot_1 + SEqHatDot_2 * SEqHatDot_2 + SEqHatDot_3 * SEqHatDot_3 + SEqHatDot_4 * SEqHatDot_4);
#     SEqHatDot_1 = SEqHatDot_1 * norm
#     SEqHatDot_2 = SEqHatDot_2 * norm
#     SEqHatDot_3 = SEqHatDot_3 * norm
#     SEqHatDot_4 = SEqHatDot_4 * norm
#
#     # compute angular estimated direction of the gyroscope error
#     w_err_x = twoSEq_1 * SEqHatDot_2 - twoSEq_2 * SEqHatDot_1 - twoSEq_3 * SEqHatDot_4 + twoSEq_4 * SEqHatDot_3
#     w_err_y = twoSEq_1 * SEqHatDot_3 + twoSEq_2 * SEqHatDot_4 - twoSEq_3 * SEqHatDot_1 - twoSEq_4 * SEqHatDot_2
#     w_err_z = twoSEq_1 * SEqHatDot_4 - twoSEq_2 * SEqHatDot_3 + twoSEq_3 * SEqHatDot_2 - twoSEq_4 * SEqHatDot_1
#
#     # compute an    w_y = w_y - w_by
#     w_z = w_z - w_bz
#
#     # compute the quaternion rate measured by gyroscopes
#     SEqDot_omega_1 = -halfSEq_2 * w_x - halfSEq_3 * w_y - halfSEq_4 * w_z
#     SEqDot_omega_2 = halfSEq_1 * w_x + halfSEq_3 * w_z - halfSEq_4 * w_y
#     SEqDot_omega_3 = halfSEq_1 * w_y - halfSEq_2 * w_z + halfSEq_4 * w_x
#     SEqDot_omega_4 = halfSEq_1 * w_z + halfSEq_2 * w_y - halfSEq_3 * w_x
#
#     # compute then integrate the estimated quaternion rate
#     SEq_1 = SEq_1 + (SEqDot_omega_1 - (beta * SEqHatDot_1)) * delta_t
#     SEq_2 = SEq_2 + (SEqDot_omega_2 - (beta * SEqHatDot_2)) * delta_t
#     SEq_3 = SEq_3 + (SEqDot_omega_3 - (beta * SEqHatDot_3)) * delta_t
#     SEq_4 = SEq_4 + (SEqDot_omega_4 - (beta * SEqHatDot_4)) * delta_t
#
#     # normalise quaternion
#     norm = 1 / math.sqrt(SEq_1 * SEq_1 + SEq_2 * SEq_2 + SEq_3 * SEq_3 + SEq_4 * SEq_4)
#     SEq_1 = SEq_1 * norm
#     SEq_2 = SEq_2 * norm
#     SEq_3 = SEq_3 * norm
#     SEq_4 = SEq_4 * norm
#
#     # compute flux in the earth frame
#     SEq_1SEq_2 = SEq_1 * SEq_2 # recompute axulirary variables
#     SEq_1SEq_3 = SEq_1 * SEq_3
#     SEq_1SEq_4 = SEq_1 * SEq_4
#     SEq_3SEq_4 = SEq_3 * SEq_4
#     SEq_2SEq_3 = SEq_2 * SEq_3
#     SEq_2SEq_4 = SEq_2 * SEq_4
#     h_x = twom_x * (0.5 - SEq_3 * SEq_3 - SEq_4 * SEq_4) + twom_y * (SEq_2SEq_3 - SEq_1SEq_4) + twom_z * (SEq_2SEq_4 + SEq_1SEq_3)
#     h_y = twom_x * (SEq_2SEq_3 + SEq_1SEq_4) + twom_y * (0.5 - SEq_2 * SEq_2 - SEq_4 * SEq_4) + twom_z * (SEq_3SEq_4 - SEq_1SEq_2)
#     h_z = twom_x * (SEq_2SEq_4 - SEq_1SEq_3) + twom_y * (SEq_3SEq_4 + SEq_1SEq_2) + twom_z * (0.5 - SEq_2 * SEq_2 - SEq_3 * SEq_3)
#
#     # normalise the flux vector to have only components in the x and z
#     b_x = math.sqrt((h_x * h_x) + (h_y * h_y))
#     b_z = h_z
#
#     return SEq_1, SEq_2, SEq_3, SEq_4, t, b_x, b_z, w_bx, w_by, w_bz
