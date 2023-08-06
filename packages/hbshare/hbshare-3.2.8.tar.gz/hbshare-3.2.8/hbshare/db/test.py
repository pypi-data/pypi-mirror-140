import hbshare as hbs
if __name__ == '__main__':
    data = hbs.commonQuery('BARRA_FACTORY', startDate='20060104', endDate='20210112')
    print(data)
