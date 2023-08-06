from robertcommonio.system.io.file import FileType, FileConfig, FileAccessor

def test_csv():
    accessor = FileAccessor(FileConfig(PATH='E:/test.csv', MODE=FileType.CSV))
    accessor.save('ss')

test_csv()