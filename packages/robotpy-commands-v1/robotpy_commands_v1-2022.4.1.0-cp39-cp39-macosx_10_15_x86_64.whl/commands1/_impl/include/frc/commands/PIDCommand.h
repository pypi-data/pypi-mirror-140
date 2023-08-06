// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#pragma once

#include <memory>
#include <string_view>

#include "frc/PIDController.h"
#include "frc/PIDOutput.h"
#include "frc/PIDSource.h"
#include "frc/commands/Command.h"

namespace frc {

/**
 * This class defines aCommand which interacts heavily with a PID loop.
 *
 * It provides some convenience methods to run an internal PIDController . It
 * will also start and stop said PIDController when the PIDCommand is first
 * initialized and ended/interrupted.
 *
 * This class is provided by the OldCommands VendorDep
 */
class PIDCommand : public Command, public PIDOutput, public PIDSource {
 public:
  PIDCommand(std::string_view name, double p, double i, double d);
  PIDCommand(std::string_view name, double p, double i, double d,
             double period);
  PIDCommand(std::string_view name, double p, double i, double d, double f,
             double period);
  PIDCommand(double p, double i, double d);
  PIDCommand(double p, double i, double d, double period);
  PIDCommand(double p, double i, double d, double f, double period);
  PIDCommand(std::string_view name, double p, double i, double d,
             Subsystem& subsystem);
  PIDCommand(std::string_view name, double p, double i, double d, double period,
             Subsystem& subsystem);
  PIDCommand(std::string_view name, double p, double i, double d, double f,
             double period, Subsystem& subsystem);
  PIDCommand(double p, double i, double d, Subsystem& subsystem);
  PIDCommand(double p, double i, double d, double period, Subsystem& subsystem);
  PIDCommand(double p, double i, double d, double f, double period,
             Subsystem& subsystem);
  ~PIDCommand() override = default;

  PIDCommand(PIDCommand&&) = default;
  PIDCommand& operator=(PIDCommand&&) = default;

  void SetSetpointRelative(double deltaSetpoint);

  // PIDOutput interface
  void PIDWrite(double output) override;

  // PIDSource interface
  double PIDGet() override;

 protected:
  std::shared_ptr<PIDController> GetPIDController() const;
  void _Initialize() override;
  void _Interrupted() override;
  void _End() override;
  void SetSetpoint(double setpoint);
  double GetSetpoint() const;
  double GetPosition();

  virtual double ReturnPIDInput() = 0;
  virtual void UsePIDOutput(double output) = 0;

 private:
  // The internal PIDController
  std::shared_ptr<PIDController> m_controller;

 public:
  void InitSendable(wpi::SendableBuilder& builder) override;
};

}  // namespace frc
