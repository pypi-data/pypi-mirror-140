// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#pragma once

#include <functional>
#include <string_view>

#include "frc/commands/Command.h"
#include "frc/commands/Subsystem.h"

namespace frc {

/**
 * This command will execute once, then finish immediately afterward.
 *
 * Subclassing InstantCommand is shorthand for returning true from IsFinished().
 *
 * This class is provided by the OldCommands VendorDep
 */
class InstantCommand : public Command {
 public:
  /**
   * Creates a new InstantCommand with the given name.
   *
   * @param name The name for this command
   */
  explicit InstantCommand(std::string_view name);

  /**
   * Creates a new InstantCommand with the given requirement.
   *
   * @param subsystem The subsystem that the command requires
   */
  explicit InstantCommand(Subsystem& subsystem);

  /**
   * Creates a new InstantCommand with the given name.
   *
   * @param name      The name for this command
   * @param subsystem The subsystem that the command requires
   */
  InstantCommand(std::string_view name, Subsystem& subsystem);

  /**
   * Create a command that calls the given function when run.
   *
   * @param func The function to run when Initialize() is run.
   */
  explicit InstantCommand(std::function<void()> func);

  /**
   * Create a command that calls the given function when run.
   *
   * @param subsystem The subsystems that this command runs on.
   * @param func      The function to run when Initialize() is run.
   */
  InstantCommand(Subsystem& subsystem, std::function<void()> func);

  /**
   * Create a command that calls the given function when run.
   *
   * @param name   The name of the command.
   * @param func   The function to run when Initialize() is run.
   */
  InstantCommand(std::string_view name, std::function<void()> func);

  /**
   * Create a command that calls the given function when run.
   *
   * @param name      The name of the command.
   * @param subsystem The subsystems that this command runs on.
   * @param func      The function to run when Initialize() is run.
   */
  InstantCommand(std::string_view name, Subsystem& subsystem,
                 std::function<void()> func);

  InstantCommand() = default;
  ~InstantCommand() override = default;

  InstantCommand(InstantCommand&&) = default;
  InstantCommand& operator=(InstantCommand&&) = default;

 protected:
  std::function<void()> m_func = nullptr;
  void _Initialize() override;
  bool IsFinished() override;
};

}  // namespace frc
