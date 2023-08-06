# KvK

KvK file handler 

Installation:
    
    $ pip install kvk

KvK file example (file.kvk):

    <#
        class "example" ::>
            (id) -> "0"
            (available) -> "true"
        class "anotherExample" ::>
            (id) -> "1"
            (accessible) -> "true"
    #>

Creation of KvK object:
    
    import kvk
    fileHandler = kvk.KvK('file.kvk')

Read a KvK file:

    fileHandler.read()
    # output: [{'example':{'id':'0', 'available':'true'}}, {'anotherExample':{'id':'1', 'accessible':'true'}}]

Write a KvK file:
    
    fileHandler.write(content=[{'newClass':{'id':'2', 'trust':'true'}}, {'anotherNewClass':{'id':'3', 'available':'true'}}]

- The file content is removed and replaced with the new content

Get a class or an attribute from file:

    fileHandler.get(element='newClass')
    # output: {'id':'2', 'trust':'true'}

    fileHandler.get(element='id', className='anotherNewClass')
    # output: 3

Add a class:

    fileHandler.addClass(className='addedClass')

- Adds the class to the end of the file

Add an attribute:

    fileHandler.addAttr(className='addedClass', attrName='addedAttribute', attrContent='first')

- The attributes are added at the top of the class, before the existing arguments

Edit a class:

    fileHandler.editClass(oldClassName='addedClass', newClassName='editedClass')
    
Edit an attribute:

    fileHandler.editAttr(className='editedClass', oldAttrName='addedAttribute', newAttrName='editedAttribute', attrContent='alwaysFirst')

- Changing the attribute content is not required

Remove a class:

    fileHandler.removeClass(className='editedClass')
- Removes both class and related attributes

Remove an attribute:

    fileHandler.removeAttr(className='anotherNewClass', attrName='available')