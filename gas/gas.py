import ROOT
import os
import sys
import ctypes
import numpy as np

try:
    ROOT.Garfield
except AttributeError as e:
    garfield_install = os.getenv("GARFIELD_INSTALL")
    print(f"Garfield Install: {garfield_install}")
    ROOT.gSystem.Load(garfield_install + "/lib/libmagboltz.so")
    ROOT.gSystem.Load(garfield_install + "/lib/libGarfield.so")
    print("Garfield Initialized!")


class Gas:
    def load_gas_file(self, gas_filename: str):
        self.gas.LoadGasFile(gas_filename)

    def __init__(self, gas_file: str = None):
        self.gas = ROOT.Garfield.MediumMagboltz()
        if gas_file:
            self.load_gas_file(gas_file)

    def print_gas(self):
        self.gas.PrintGas()

    @property
    def name(self):
        return self.gas.GetName()

    @property
    def temperature(self):
        # Value in Kelvin
        return self.gas.GetTemperature()

    @temperature.setter
    def temperature(self, value_in_kelvin: float):
        self.gas.SetTemperature(value_in_kelvin)

    __torr_to_bar = 0.0013332237

    @property
    def pressure(self):
        # Value in Bar
        return self.gas.GetPressure() * self.__torr_to_bar

    @pressure.setter
    def pressure(self, value_in_bar: float):
        self.gas.SetPressure(value_in_bar / self.__torr_to_bar)

    def __repr__(self):
        representation = f"Gas: '{self.name}' - Pressure: {self.pressure:0.2f} Bar - Temperature: {self.temperature:0.2f} K"
        return representation

    def __get_drift_velocity(self, electric_field: float, pressure: float = None, temperature: float = None) -> float:
        starting_pressure, starting_temperature = self.pressure, self.temperature

        if not pressure:
            pressure = self.pressure
        else:
            self.pressure = pressure

        if not temperature:
            temperature = self.temperature
        else:
            self.temperature = temperature

        vz = ctypes.c_double()
        self.gas.ElectronVelocity(0, 0, -electric_field,  # Electric field
                                  0, 0, 0,  # Magnetic field (zero)
                                  ctypes.c_double(), ctypes.c_double(), vz  # Drift velocity in cm/us (we only need vz)
                                  )

        if self.pressure != starting_pressure: self.pressure = starting_pressure
        if self.temperature != starting_temperature: self.temperature = starting_temperature

        return vz.value

    def get_drift_velocity_electric_field(self, electric_field: np.array, pressure: float = None,
                                          temperature: float = None) -> np.array:
        velocity = np.zeros(len(electric_field))
        for i in range(len(velocity)):
            velocity[i] = self.__get_drift_velocity(electric_field=electric_field[i], pressure=pressure,
                                                    temperature=temperature)
        return velocity

    def get_drift_velocity_pressure(self, electric_field: float, pressure: np.array,
                                    temperature: float = None) -> np.array:
        velocity = np.zeros(len(pressure))
        for i in range(len(velocity)):
            velocity[i] = self.__get_drift_velocity(electric_field=electric_field, pressure=pressure[i],
                                                    temperature=temperature)
        return velocity

    def get_drift_velocity_temperature(self, electric_field: float, temperature: np.array,
                                       pressure: float = None) -> np.array:
        velocity = np.zeros(len(temperature))
        for i in range(len(velocity)):
            velocity[i] = self.__get_drift_velocity(electric_field=electric_field, pressure=pressure,
                                                    temperature=temperature[i])
        return velocity
