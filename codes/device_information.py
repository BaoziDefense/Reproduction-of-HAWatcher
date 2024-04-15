#显示设备的名称、属性、值范围、当前值、
#由于一开始设备都关着，所以设备的值（除了温度感应器）一开始都为关
devices = {
    'M001': {'type': 'Motion Sensor', 'attribute': 'motion', 'range': ['ON', 'OFF'],'value':'OFF'},
    'M002': {'type': 'Motion Sensor', 'attribute': 'motion', 'range': ['ON', 'OFF'],'value':'OFF'},
    'M003': {'type': 'Motion Sensor', 'attribute': 'motion', 'range': ['ON', 'OFF'],'value':'OFF'},
    'M004': {'type': 'Motion Sensor', 'attribute': 'motion', 'range': ['ON', 'OFF'],'value':'OFF'},
    'M007': {'type': 'Motion Sensor', 'attribute': 'motion', 'range': ['ON', 'OFF'],'value':'OFF'},
    'M008': {'type': 'Motion Sensor', 'attribute': 'motion', 'range': ['ON', 'OFF'],'value':'OFF'},
    'M011': {'type': 'Motion Sensor', 'attribute': 'motion', 'range': ['ON', 'OFF'],'value':'OFF'},
    'M022': {'type': 'Motion Sensor', 'attribute': 'motion', 'range': ['ON', 'OFF'],'value':'OFF'},

    'D001': {'type': 'Door Sensor', 'attribute': 'door', 'range': ['OPEN', 'CLOSE'],'value':'CLOSE'},
    'D002': {'type': 'Door Sensor', 'attribute': 'door', 'range': ['OPEN', 'CLOSE'],'value':'CLOSE'},

    'T101': {'type': 'Temperature Sensor', 'attribute': 'temperature', 'range': None,'value':'32'},
    'T102': {'type': 'Temperature Sensor', 'attribute': 'temperature', 'range': None,'value':'24'},
    'T103': {'type': 'Temperature Sensor', 'attribute': 'temperature', 'range': None,'value':'24'},
    'T104': {'type': 'Temperature Sensor', 'attribute': 'temperature', 'range': None,'value':'26'},
    'T105': {'type': 'Temperature Sensor', 'attribute': 'temperature', 'range': None,'value':'23'},
    'T106': {'type': 'Temperature Sensor', 'attribute': 'temperature', 'range': None,'value':'25'},

    'L001': {'type': 'Light', 'attribute': 'lightingMode', 'range': ['ON', 'OFF'],'value':'OFF'},
    'L002': {'type': 'Light', 'attribute': 'lightingMode', 'range': ['ON', 'OFF'],'value':'OFF'},
    'L003': {'type': 'Light', 'attribute': 'lightingMode', 'range': ['ON', 'OFF'],'value':'OFF'},
    'L004': {'type': 'Light', 'attribute': 'lightingMode', 'range': ['ON', 'OFF'],'value':'OFF'},

    'Fan1': {'type': 'Fan', 'attribute': 'fanMode', 'range': ['ON', 'OFF'],'value':'ON'},
    'Fan2': {'type': 'Fan', 'attribute': 'fanMode', 'range': ['ON', 'OFF'],'value':'OFF'},
    'Fan3': {'type': 'Fan', 'attribute': 'fanMode', 'range': ['ON', 'OFF'],'value':'ON'}
}

if __name__ =="__main__":
    print(devices["Fan1"]["range"])
    print(devices["T101"]["range"])
