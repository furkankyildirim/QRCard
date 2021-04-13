def readTxt():
    txt = open('./config.txt','r').readlines()
    config={}

    for line in txt:
        data = line.replace(' ','').replace('\n','').split(':')
        key = data[0]
        value = data[1]

        for i in range(2,len(data)):
            value = value + ':' + data[i] 

        config[key] = value
    return config