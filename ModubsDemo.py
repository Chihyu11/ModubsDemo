#!/usr/bin/env python3

#Demo zum auslesen eines Modbusservers

import time
import os
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder, Endian
from datetime import datetime

def readModbusAllTCP(count: int = 25, ip: str = "10.0.1.1"):
    """Liest alle Modbus Register ab 0 und decodiert die Register,
        die Daten werden unter Messwerte (list) gespeichert

    Args:
        count (int): Gibt die Anzahl Adressen an welche ausgelesen werden sollen.
            Der Standartwert ist 25.
        ip (str): Ip Adresse zu Modbus-Server. Der Standartwert ist 10.0.1.1
    Returns:
            None

    Notes:
        Für jede Ip sollte ein separater Prozess(schneller) oder Threed(ressourcensparend) gestartet werden

    Examples:
        >>> readModbusAllTCP()
        None
        >>> readModbusAllTCP(0, "10.0.1.1")
        None
    """

    client = connectToModbusClient(ip)

    while client.is_socket_open():
        res = client.read_input_registers(
            0, count=count, unit=1)  # 0-25 (Parkem)
        assert not res.isError()
        decodeModbusValues(res)
        # print(res.registers)
        time.sleep(.5)  # 500ms

def connectToModbusClient(ip: str) -> ModbusClient:
    """Stellt eine Verbindung zum Modubsserver her.

    Args:
        ip (str): Ip Adresse zu Modbus-Server.

    Returns:
            ModbusClient (pymodbus)

    Notes:
        Falls die Verbindung nicht hergestellt werden kann wird alle 10 sec einen neuer Versuch unternommen.
        Zwischen 18:00 und 6:00 beträgt die Wartezeit 600 sec(10 min)

    Examples:
        >>> connectToModbusClient("10.0.1.1")
        None
    """
    run = True
    while run:
        try:
            client = ModbusClient(ip, port=502)
            print("Verbindung zu " + ip + " wird hergestellt")
            assert client.connect()
        except AssertionError:
            print(ip + " ist offline")

        if client.is_socket_open():
            run = False
            return client
        else:
            if datetime.now().hour >= 18 or datetime.now().hour <= 6:
                time.sleep(600)  # 10 min
            else:
                time.sleep(10)  # 10 Sec


def decodeModbusValues(res):
    # Clear Ausgabe
    os.system('cls' if os.name == 'nt' else "printf '\033c'")

    # Decodiert ModbusRegister 
    CoNr = decodeCoNr(res.registers)
    print("CoNr: " + CoNr)

    Pos = decodeFlot(res.registers[20])
    print("Pos.: " + str(Pos))

    IstKraft = decodeInt(res.registers[21])
    print("IstKraft.: " + str(IstKraft))

def decodeCoNr(register: list) -> str:
    # Decodiert einen String und erstellt die richtige Reienfolge
    coNr = ""
    for i in range(0, 3):
        a = decimalToHex(register[i])
        b = hexToString(a)
        coNr = coNr + _turnOverString(b)
    if len(coNr) == 0:
        return "unknow"
    return coNr


def decodeFlot(decimalValue) -> float:
    if decimalValue is None:
        return 0.0
    return hexToFloat(decimalToHex(decimalValue))


def decodeInt(decimalValue) -> int:
    # wandelt einen Decimal Wert in int um, ignoriert werden Werrte über 1000kg und Negativwerte
    # return value int
    toReturn = decimalValue * 0.1
    if toReturn <= 1000 and toReturn >= 0:
        return toReturn
    else:
        return 0


def hexToFloat(hexValue) -> float:
    # convert hex to float
    # return value float 0.0
    if hexValue is None:
        return 0.0
    return float.fromhex(hexValue) / 100


def decimalToHex(decimalValue) -> str:
    # convert Modbus decimal value zu hex
    # return value string zb. 16640d => 4100h
    if decimalValue > 0:
        return hex(decimalValue)[2:]


def hexToString(hexValue) -> str:
    # Convert Hex to ascii
    # return value string ascii
    return bytes.fromhex(hexValue).decode('ascii')


def hexIeee754ToFloat(value) -> float:
    # Convertiert IEEE754 zu einem Float 32bit
    # return value float
    # pymodbus hat auch einen eigenen Decoder =>
    decoder = BinaryPayloadDecoder.fromRegisters(value.registers,
                                                 byteorder=Endian.Big,
                                                 wordorder=Endian.Little)
    return decoder.decode_32bit_float()


def _turnOverString(value: str) -> str:
    # Dreht string um, werden teils rückwerts ausgelsen
    return value[1] + value[0]


if __name__ == '__main__':
    # starte Modbus Scan
    readModbusAllTCP()


