class KvK:
    def __init__(self, filePath):
        self.filePath = filePath
        self.__startingContent__()
        self.pos = 0

    # private methods
    def __startingContent__(self):
        if not self.filePath[len(self.filePath) - 4: len(self.filePath)] == '.kvk':
            raise Exception('File extension must be \".kvk\"')
        else:
            try:
                self.file = open(self.filePath, 'r')
            except:
                self.content = '<#\n#>'
            else:
                self.content = self.file.read()

    def __getClass__(self):
        tmpDict = {}
        self.pos += 5
        while self.text[self.pos] == ' ':
            self.pos += 1
        if self.text[self.pos] == '"':
            self.pos += 1
            className = ''
            while self.text[self.pos] != '"':
                className += self.text[self.pos]
                self.pos += 1
            self.pos += 2
            self.insideDict = {}
            if self.text[self.pos:self.pos + 3] == '::>':
                self.pos += 3
                while self.text[self.pos:self.pos + 2] != '#>' and self.text[self.pos:self.pos + 5] != 'class':
                    if self.text[self.pos] == ' ' or self.text[self.pos] == '\t' or self.text[self.pos] == '\n':
                        self.pos += 1
                    elif self.text[self.pos] == '(':
                        self.__attr__()
                    tmpDict[className] = self.insideDict
                return tmpDict
            else:
                raise SyntaxError('Expected "::>" after class name.')
        else:
            raise SyntaxError('Expected \'\"\' after class declaration.')

    def __attr__(self):
        self.pos += 1
        attrName = ''
        while self.text[self.pos] == ' ' or self.text[self.pos] == '\t' or self.text[self.pos] == '\n':
            self.pos += 1
        while self.text[self.pos] != ')':
            attrName += self.text[self.pos]
            self.pos += 1
        self.pos += 1
        while self.text[self.pos] == ' ' or self.text[self.pos] == '\t' or self.text[self.pos] == '\n':
            self.pos += 1
        if self.text[self.pos:self.pos + 2] == '->':
            self.pos += 2
            while self.text[self.pos] == ' ':
                self.pos += 1
            if self.text[self.pos] == '"':
                attr = ''
                self.pos += 1
                while self.text[self.pos] != '"':
                    attr += self.text[self.pos]
                    self.pos += 1
                self.insideDict[attrName] = attr
                self.pos += 1
            else:
                raise SyntaxError('Expected '"' after ->")
        else:
            raise SyntaxError('Expected -> after attribute name')

    def __replaceAtIndex__(self, text, index1, index2, newContent):
        return text[0:index1] + newContent + text[index2:len(text)]

    def __insertAtIndex__(self, text, index1, toInsert):
        return text[0:index1 + 1] + toInsert + text[index1 + 2:len(text)]

    def __repr__(self):
        return f'< KvK handle class >'

    def __str__(self):
        return '< KvK handle class >'

    # public methods
    def read(self):
        try:
            with open(self.filePath, 'r') as fp:
                self.text = fp.read()
        except:
            raise Exception(f'Cannot read the file. \"{self.filePath}\" not existing yet.')
        res = []
        if self.text[self.pos:self.pos + 2] == '<#':
            self.pos += 2
            while self.pos < len(self.text):
                if self.text[self.pos] == ' ' or self.text[self.pos] == '\t' or self.text[self.pos] == '\n':
                    self.pos += 1
                if self.text[self.pos:self.pos + 5] == 'class':
                    point = self.__getClass__()
                    res.append(point)
                if self.text[self.pos:len(self.text)] == '#>':
                    break
            return res

    def get(self, element, className=None):
        self.pos = 0
        dict = self.read()
        found = False
        if className == None:
            for classCont in dict:
                for classname in classCont:
                    if classname == element:
                        found = True
                        return classCont[classname]
        else:
            for classCont in dict:
                for classname in classCont:
                    if classname == className:
                        for attr in classCont[classname]:
                            if attr == element:
                                return classCont[classname][attr]
                            else:
                                return found

    def write(self, content):
        toWrite = ''
        toWrite += '<#\n'
        for classCont in content:
            for className in classCont:
                toWrite += f'    class "{className}" ::>\n'
                for attr in classCont[className]:
                    tmp = classCont[className]
                    cont = ''
                    for content in classCont[className][attr]:
                        cont += content
                    toWrite += f'        ({attr}) -> "{cont}"\n'
                # toWrite += '\n'
        toWrite += '#>'
        self.file.write(toWrite)

    def addClass(self, className):
        newContent = self.__replaceAtIndex__(str(self.content), len(self.content) - 3, len(self.content) - 2,
                                             f'\n    class "{className}" ::>\n')
        self.content = newContent
        with open(str(self.filePath), 'w') as file:
            file.write(newContent)

    def addAttr(self, className, attrName, attrContent):
        try:
            index = self.content.index(f'class "{className}" ::>')
        except:
            raise Exception('Class not found')
        else:
            endIndex = (index + (len(f'class "{className}" ::>'))) - 1
            newContent = self.__insertAtIndex__(self.content, endIndex, f'\n        ({attrName}) -> "{attrContent}"\n')
            self.content = newContent
            with open(self.filePath, 'w') as file:
                file.write(newContent)

    def editClass(self, oldClassName, newClassName):
        try:
            index = self.content.index(f'class "{oldClassName}" ::>')
        except:
            raise Exception('Class not found. You might want to use "addClass" function to add it to the file.')
        else:
            startIndex = index + 7
            endIndex = startIndex + len(oldClassName)
            self.content = self.content[0:startIndex] + newClassName + self.content[endIndex:len(self.content)]

            with open(self.filePath, 'w') as file:
                file.write(self.content)

    def editAttr(self, className, oldAttrName, newAttrName, attrContent=None):
        try:
            classIndex = self.content.index('class \"' + className + '\" ::>')
        except:  # se non trova la classe
            raise Exception('Class not found')
        else:  # se trova la classe
            preClass = self.content[0:classIndex]  # prima della classe
            tmp = self.content[classIndex + 5:len(self.content)]
            try:
                endClassIndex = tmp.index('class')
            except:
                endClassIndex = tmp.index('#>')
            isolatedClass = self.content[classIndex:endClassIndex + classIndex + 5]  # classe isolata
            afterClass = tmp[endClassIndex:len(tmp)]  # self.content[endClassIndex:len(self.content)] # dopo la classe

            try:
                oldAttrIndex = isolatedClass.index(oldAttrName)
            except:
                raise Exception('Attribite not found')
            else:
                isolatedClass = isolatedClass[0:oldAttrIndex] + newAttrName + isolatedClass[
                                                                              oldAttrIndex + len(oldAttrName):len(
                                                                                  isolatedClass)]
                if (attrContent != None):
                    virgStart = oldAttrIndex
                    while isolatedClass[virgStart] != '"':
                        virgStart += 1
                    virgEnd = virgStart + 1
                    while isolatedClass[virgEnd] != '"':
                        virgEnd += 1
                    isolatedClass = isolatedClass[0:virgStart + 1] + attrContent + isolatedClass[
                                                                                   virgEnd:len(isolatedClass)]
                self.content = preClass + isolatedClass + afterClass
                with open(self.filePath, 'w') as file:
                    file.write(self.content)

    def removeClass(self, className):
        try:
            classIndex = self.content.index('class \"' + className + '\" ::>')
        except:  # se non trova la classe
            raise Exception('Class not found')
        else:  # se trova la classe
            preClass = self.content[0:classIndex - 4]  # prima della classe
            tmp = self.content[classIndex + 5:len(self.content)]
            try:
                endClassIndex = tmp.index('class')
            except:
                endClassIndex = tmp.index('#>')
                afterClass = '#>'
            else:
                afterClass = tmp[
                             endClassIndex:len(tmp)]  # self.content[endClassIndex:len(self.content)] # dopo la classe
            self.content = preClass + afterClass
            with open(self.filePath, 'w') as file:
                file.write(self.content)

    def removeAttr(self, className, attrName):
        try:
            classIndex = self.content.index('class \"' + className + '\" ::>')
        except:  # se non trova la classe
            raise Exception('Class not found')
        else:  # se trova la classe
            preClass = self.content[0:classIndex]  # prima della classe
            tmp = self.content[classIndex + 5:len(self.content)]
            try:
                endClassIndex = tmp.index('class')
            except:
                endClassIndex = tmp.index('#>')
            isolatedClass = self.content[classIndex:endClassIndex + classIndex + 5]  # classe isolata
            afterClass = tmp[endClassIndex:len(tmp)]  # self.content[endClassIndex:len(self.content)] # dopo la classe
            try:
                attrIndex = isolatedClass.index(attrName)
            except:
                raise Exception('Attribute not found')
            else:
                tmp = isolatedClass[0:attrIndex - 1] + isolatedClass[attrIndex + len(attrName):len(isolatedClass)]
                print(tmp)
                virgStart = attrIndex
                while tmp[virgStart] != '"':
                    virgStart += 1
                virgEnd = virgStart + 1
                while tmp[virgEnd] != '"':
                    virgEnd += 1
                isolatedClass = isolatedClass[0:attrIndex - 10] + isolatedClass[virgEnd + 5:len(
                    isolatedClass)]  # isolatedClass[0:virgStart+1] +
                print(isolatedClass)
                self.content = preClass + isolatedClass + afterClass
                with open(self.filePath, 'w') as file:
                    file.write(self.content)
