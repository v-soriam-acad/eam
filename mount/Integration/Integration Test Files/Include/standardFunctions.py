# 
#      * Copyright (c)2008-2012 Enterprise Architecture Solutions ltd.
#      * This file is part of Essential Architecture Manager, 
#      * the Essential Architecture Meta Model and The Essential Project.
#      *
#      * Essential Architecture Manager is free software: you can redistribute it and/or modify
#      * it under the terms of the GNU General Public License as published by
#      * the Free Software Foundation, either version 3 of the License, or
#      * (at your option) any later version.
#      *
#      * Essential Architecture Manager is distributed in the hope that it will be useful,
#      * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      * but WITHOUT ANY WARRANTY; without even the implied warranty of
#      * GNU General Public License for more details.
#      *
#      * You should have received a copy of the GNU General Public License
#      * along with Essential Architecture Manager.  If not, see <http://www.gnu.org/licenses/>.
#      * 
#       
# 19.02.2008	JWC v1.0
# 20.05.2008	JWC v1.0
# 22.05.2008	JWC v1.0 released Create or Update instances and Attributes
# 15.07.2008	JWC v1.1 Added new functions for finding instances by name in Essential.
# 17.07.2008	JWC	v1.1.1 fixed matching issue in getEssentialInstanceContainsIgnoreCase()
# 11.08.2008	JWC	v1.2 Added new functions (2) to match instance names more accurately
# 04.09.2008	JWC	v1.2.1 Updated addIfNotThere() function to ensure multiple values are not 
#						 added to single-cardinality slots. Added setSlot() function to enable this
# 20.03.2009	JWC	v1.3 Added support for importing / synchronising EA_Relation and :EA_Graph_Relation instances
# 20.03.2009	JWC	v1.3.1 Fixed the handling of the 3 name slot variants
# 20.09.2011    JWC v1.4 Handle graph relations that have no :relation_name value in the source.
# 04.10.2011    JWC v1.5 Migrated to .py, handle non-existent slots.
# 31.10.2011    JWC v1.6 Moved guard code to addIfNotThere() and setSlot() to avoid null instance.
# 28.09.2012    JWC v1.7 Changed the progress printing to remove names / external references used to support Unicode.
# 19.11.2012    JWC v1.8 Added new Instance creating and getting functions.
# 21.11.2012    JWC v1.9 Added the EssentialGetInstance() function to intelligently find the correct instance
# 12.12.2012    JWC v1.10 Added the GetActorToRole() function
# 
# Essential(tm) Architecture Manager
# Standard set of functions to be used by the integration/import scripts
#

from java.util import Date
from java.text import DateFormat

# Get a reference to the instance of the specified class that has the specified external reference in the
# specified external repository. If such an instance cannot be found, create one with the specified 
# name (real name, not instance name)
# theClassName - the name of the Essential meta class
# theExternalRef - the unique reference/instance ID of the element in the external repository
# theExternalRepository - the name of the external repository
# theInstanceName - the name of the instance that is being created/updated in the integration
def getEssentialInstance(theClassName, theExternalRef, theExternalRepository, theInstanceName):
	anInstList = kb.getCls(theClassName).getDirectInstances()
	for anInst in anInstList:
		anExternalRefList = anInst.getDirectOwnSlotValues(kb.getSlot("external_repository_instance_reference"))
		if anExternalRefList != None:
			anExternalRef = getExternalRefInst(anExternalRefList, getExternalRepository(theExternalRepository))
			if anExternalRef != None:
				anExternalID = anExternalRef.getDirectOwnSlotValue(kb.getSlot("external_instance_reference"))
				if(anExternalID == theExternalRef):
					anExternalRef.setOwnSlotValue(kb.getSlot("external_update_date"), timestamp())
					print "Updated instance via name match, on class: " + theClassName
					return anInst
	# if we're here, we haven't found one, so create one
	aNewInst = kb.createInstance(None, kb.getCls(theClassName))
	anExternalRef = createExternalRefInst(theExternalRepository, theExternalRef)
	
	# Handle the 3 variants of name
	aNameSlot = getNameSlot(aNewInst)
	aNewInst.setOwnSlotValue(kb.getSlot(aNameSlot), theInstanceName)	
	aNewInst.addOwnSlotValue(kb.getSlot("external_repository_instance_reference"), anExternalRef)
	print "Created new instance of class: " + theClassName
	return aNewInst

# Return the external reference that applied to the specified External Repository from a list 
# of external references from an Essential instance.
# theExternalRefList - the list of external reference records for an EssentialInstance
# theExternalRepository - the instance of the external repository	
def getExternalRefInst(theExternalRefList, theExternalRepository):
	# Search the list looking for the entry about the specified External Repository
	for aRef in theExternalRefList:
		if(aRef.getDirectOwnSlotValue(kb.getSlot("external_repository_reference")) == theExternalRepository):
			return aRef

# Create a new External Reference record to be associated with an Essential instance.
# theExternalRepository - the name (a String) of the external repository
# theExternalReference - the reference ID that is used in the specified external repository
def createExternalRefInst(theExternalRepositoryName, theExternalReference):
	aNewExternalRef = kb.createInstance(None, kb.getCls("External_Instance_Reference"))
	aNewExternalRef.setOwnSlotValue(kb.getSlot("name"), theExternalRepositoryName + "::" + theExternalReference)
	aNewExternalRef.addOwnSlotValue(kb.getSlot("external_repository_reference"), getExternalRepository(theExternalRepositoryName))
	aNewExternalRef.setOwnSlotValue(kb.getSlot("external_instance_reference"), theExternalReference)
	aNewExternalRef.setOwnSlotValue(kb.getSlot("external_update_date"), timestamp())
	return aNewExternalRef

# Get a reference to the instance of External_Repository that has the specified name
# theExternalRepositoryName - the name of the external repository
def getExternalRepository(theExternalRepositoryName):
	anExternalRepositoryList = kb.getCls("External_Repository").getDirectInstances()
	for anExtRepos in anExternalRepositoryList:
		if(anExtRepos.getDirectOwnSlotValue(kb.getSlot("name")) == theExternalRepositoryName):
			return anExtRepos
	# report error if not found
	print "Repository: " + theExternalRepositoryName + " not defined as an external repository for integration in this EssentialAM model"
			
# Return a string of the current date/time to be used for timestamping.
def timestamp():
	return DateFormat.getDateTimeInstance().format(Date())
	
# Update the named attribute associated with the specified technology instance object
# or create it if it's not already been defined
def setOrUpdateTechInstAttributeByName(theAttributeName, theAttributeValue, theInstance):
	anAttributeList = kb.getCls("Attribute").getDirectInstances()
	aFoundAttribute = None
	for anAttribute in anAttributeList:
		if(anAttribute.getDirectOwnSlotValue(kb.getSlot("name")) == theAttributeName):
			aFoundAttribute = anAttribute
	anAttributeValList = theInstance.getDirectOwnSlotValues(kb.getSlot("technology_instance_attributes"))
	for anAttributeVal in anAttributeValList:
		if(anAttributeVal.getDirectOwnSlotValue(kb.getSlot("attribute_value_of")) == aFoundAttribute):
			anAttributeVal.setOwnSlotValue(kb.getSlot("attribute_value"), theAttributeValue)
			anAttributeVal.setOwnSlotValue(kb.getSlot("name"), theAttributeName + " = " + theAttributeValue)
			return
	# Else this instance has no attribute value defined for this attribute
	aNewAV = kb.createInstance(None, kb.getCls("Attribute_Value"))
	aNewAV.addOwnSlotValue(kb.getSlot("attribute_value_of"), aFoundAttribute)
	aNewAV.setOwnSlotValue(kb.getSlot("attribute_value"), theAttributeValue)
	aNewAV.setOwnSlotValue(kb.getSlot("name"), theAttributeName + " = " + theAttributeValue)
	theInstance.addOwnSlotValue(kb.getSlot("technology_instance_attributes"), aNewAV)
		
# Update the named attribute associated with the specified technology Node (theInstance) object
# or create it if it's not already been defined
def setOrUpdateTechNodeAttributeByName(theAttributeName, theAttributeValue, theInstance):
	anAttributeList = kb.getCls("Attribute").getDirectInstances()
	aFoundAttribute = None
	for anAttribute in anAttributeList:
		if(anAttribute.getDirectOwnSlotValue(kb.getSlot("name")) == theAttributeName):
			aFoundAttribute = anAttribute
	anAttributeValList = theInstance.getDirectOwnSlotValues(kb.getSlot("technology_node_attributes"))
	for anAttributeVal in anAttributeValList:
		if(anAttributeVal.getDirectOwnSlotValue(kb.getSlot("attribute_value_of")) == aFoundAttribute):
			anAttributeVal.setOwnSlotValue(kb.getSlot("attribute_value"), theAttributeValue)
			anAttributeVal.setOwnSlotValue(kb.getSlot("name"), theAttributeName + " = " + theAttributeValue)
			return
	# Else this instance has no attribute value defined for this attribute
	aNewAV = kb.createInstance(None, kb.getCls("Attribute_Value"))
	aNewAV.addOwnSlotValue(kb.getSlot("attribute_value_of"), aFoundAttribute)
	aNewAV.setOwnSlotValue(kb.getSlot("attribute_value"), theAttributeValue)
	aNewAV.setOwnSlotValue(kb.getSlot("name"), theAttributeName + " = " + theAttributeValue)
	theInstance.addOwnSlotValue(kb.getSlot("technology_node_attributes"), aNewAV)

# Set a slot value to the specified value. To be used with single-cardinality slots
# only
# theInstance - the instance to which we wish to set the slot to contain theInstanceToAdd
# theSlotName - the name of the slot on theInstance
# theInstanceToAdd - the instance to set in theSlotName slot on theInstance
# 04.10.2011 JWC - check that slot exists first
# 31.10.2011 JWC - Guard code, Check theInstance != None
def setSlot(theInstance, theSlotName, theInstanceToAdd):
    if theInstance == None:
        return
    aSlot = kb.getSlot(theSlotName)
    if aSlot != None:
        theInstance.setOwnSlotValue(aSlot, theInstanceToAdd)
    else:
        print "WARNING: Attempt to set non-existent slot: " + theSlotName

# Add the slot value to the specified instance only if it's not already there.
# theInstance - the instance to which we wish to add theInstanceToAdd
# theSlotName - the name of the slot on theInstance
# theInstanceToAdd - the instance to add to theSlotName slot on theInstance
# v1.2.1: If theSlotName is a single cardinality slot, use setSlot()
# 04.10.2011 JWC - check that the slot exists first
# 31.10.2011 JWC - Guard code, Check theInstance != None
def addIfNotThere(theInstance, theSlotName, theInstanceToAdd):
    if theInstance == None:
        return
    aSlot = kb.getSlot(theSlotName)
    if aSlot != None:
        if aSlot.getAllowsMultipleValues():
            anInstList = theInstance.getDirectOwnSlotValues(kb.getSlot(theSlotName))
            for anInst in anInstList:
                if anInst == theInstanceToAdd:
                    return
            # else we haven't got this already, so add it
            theInstance.addOwnSlotValue(kb.getSlot(theSlotName), theInstanceToAdd)
        else:
            setSlot(theInstance, theSlotName, theInstanceToAdd)
    else:
        print "WARNING: Attempt to set non-existent slot: " + theSlotName

# Find the instance by a contains case-sensitive match on the instance name in Essential repository
# Use this for getting instances that are expected to already be in the repository
# If not found, create a new one.
# theClassName - the Essential class for the instance
# theExternalRef - the External Reference ID for this instance
# theExternalRepository - the External Repository that theExternalRef applies to
# theInstanceName - the name of the instance in the Essential Repository
def getEssentialInstanceContains(theClassName, theExternalRef, theExternalRepository, theInstanceName):
    # 20.09.2011 JWC - handle empty theInstanceName
    if theInstanceName == "":
        theInstanceName = theExternalRef
        print "Handling empty instance name for " + theExternalRef
    
    # 20.09.2011 JWC - Make sure that the source class is in the targert repository
    aCls = kb.getCls(theClassName)    
    # if not-report a warning and skip that instance.
    if aCls == None:
        print "WARNING: Skipping instance of unknown class: " + theClassName + " : " + theInstanceName
        return None
    
    anInstList = kb.getCls(theClassName).getDirectInstances()
    for anInst in anInstList:
        anExternalRefList = anInst.getDirectOwnSlotValues(kb.getSlot("external_repository_instance_reference"))
        if anExternalRefList != None:	
            anExternalRef = getExternalRefInst(anExternalRefList, getExternalRepository(theExternalRepository))
            if anExternalRef != None:
                anExternalID = anExternalRef.getDirectOwnSlotValue(kb.getSlot("external_instance_reference"))
                if(anExternalID == theExternalRef):
                    anExternalRef.setOwnSlotValue(kb.getSlot("external_update_date"), timestamp())
                    print "Updated Instance via External Reference on class: " + theClassName
                    return anInst

	# If we're here, this external reference hasn't been found.
	# Try to find by instance_name and case sensitive
    aNameSlot = getNameSlotForClass(theClassName)
    for anInst in anInstList:
        aName = anInst.getDirectOwnSlotValue(kb.getSlot(aNameSlot))
		
        if aName != None:
            if(aName.find(theInstanceName) != -1):
                # We have found a match
                anExternalRef = createExternalRefInst(theExternalRepository, theExternalRef)
                anInst.addOwnSlotValue(kb.getSlot("external_repository_instance_reference"), anExternalRef)
                print "Updated instance via name match, on class: " + theClassName
                return anInst
				
    # if we're here, we haven't found one, so create one
    aNewInst = kb.createInstance(None, kb.getCls(theClassName))
	
	# Handle the 3 variants of name
	#aNameSlot = getNameSlot(aNewInst)
    aNewInst.setOwnSlotValue(kb.getSlot(aNameSlot), theInstanceName)	
				
    anExternalRef = createExternalRefInst(theExternalRepository, theExternalRef)
    aNewInst.addOwnSlotValue(kb.getSlot("external_repository_instance_reference"), anExternalRef)
    print "Created new instance of class: " + theClassName
    return aNewInst

# Find the instance by a contains match - ignoring case - on the instance name in Essential repository
# Use this for getting instances that are expected to already be in the repository. Use theMatchString
# to specify the string to use as a match on existing instances.
# If not found, create a new one.
# theClassName - the Essential class for the instance
# theExternalRef - the External Reference ID for this instance
# theExternalRepository - the External Repository that theExternalRef applies to
# theInstanceName - the name of the instance in the Essential Repository
# theMatchString - the string that should be used to match against and find the instance
def getEssentialInstanceContainsIgnoreCase(theClassName, theExternalRef, theExternalRepository, theInstanceName, theMatchString):
	anInstList = kb.getCls(theClassName).getDirectInstances()
	for anInst in anInstList:
		anExternalRefList = anInst.getDirectOwnSlotValues(kb.getSlot("external_repository_instance_reference"))
		if anExternalRefList != None:	
			anExternalRef = getExternalRefInst(anExternalRefList, getExternalRepository(theExternalRepository))
			if anExternalRef != None:
				anExternalID = anExternalRef.getDirectOwnSlotValue(kb.getSlot("external_instance_reference"))
				if(anExternalID == theExternalRef):
					anExternalRef.setOwnSlotValue(kb.getSlot("external_update_date"), timestamp())
					print "Updated Instance via External Reference on class: " + theClassName
					return anInst
					
	# If we're here, this external reference hasn't been found.
	# Try to find by instance_name - ignoring case of each
	aNameSlot = getNameSlotForClass(theClassName)
	for anInst in anInstList:
		aName = anInst.getDirectOwnSlotValue(kb.getSlot(aNameSlot))
		if aName != None:
			aName = aName.lower()
			aMatchName = theMatchString.lower()
			if((aName.find(aMatchName) != -1) or (aMatchName.find(aName) != -1)):
				# We have found a match
				anExternalRef = createExternalRefInst(theExternalRepository, theExternalRef)
				anInst.addOwnSlotValue(kb.getSlot("external_repository_instance_reference"), anExternalRef)
				print "Updated instance via name match, on class: " + theClassName
				return anInst
				
	# if we're here, we haven't found one, so create one
	aNewInst = kb.createInstance(None, kb.getCls(theClassName))
	aNewInst.setOwnSlotValue(kb.getSlot(aNameSlot), theInstanceName)			
	anExternalRef = createExternalRefInst(theExternalRepository, theExternalRef)
	aNewInst.addOwnSlotValue(kb.getSlot("external_repository_instance_reference"), anExternalRef)
	print "Created new instance of class: " + theClassName
	return aNewInst
	
# Define a new External Repository or ignore definition if the repository is already known
# theExternalRepository - the name of the external repository
def defineExternalRepository(theExternalRepository, theDescription):
	anInstanceList = kb.getCls("External_Repository").getDirectInstances()
	for anInstance in anInstanceList:
		aName = anInstance.getDirectOwnSlotValue(kb.getSlot("name"))
		if aName != None:
			if(aName == theExternalRepository):
				# We've found it, it's defined already
				return anInstance
				
	# if we're here it's not defined, so define it.
	aNewRepos = kb.createInstance(None, kb.getCls("External_Repository"))
	aNewRepos.setOwnSlotValue(kb.getSlot("name"), theExternalRepository)
	aNewRepos.setOwnSlotValue(kb.getSlot("description"), theDescription)
	return aNewRepos
	
# Function to add a new Attribute instance to the Essential model.
# theName - the name of the Attribute
# theDescription - a description of the attribute
# theUnit - the units of the attribute value, e.g. MB, Mbps, kg or '_' or space if not applicable
def addNewEAMAttribute(theName, theDescription, theUnit):
	anAttributeList = kb.getCls("Attribute").getDirectInstances()
	aFoundAttribute = None
	for anAttribute in anAttributeList:
		if(anAttribute.getDirectOwnSlotValue(kb.getSlot("name")) == theName):
			aFoundAttribute = anAttribute
			break
	if aFoundAttribute == None:
		aNewAttribute = kb.createInstance(None, kb.getCls("Attribute"))
		aNewAttribute.setOwnSlotValue(kb.getSlot("name"), theName)
		aNewAttribute.setOwnSlotValue(kb.getSlot("description"), theDescription)
		aNewAttribute.setOwnSlotValue(kb.getSlot("attribute_value_unit"), theUnit)

# Function to find Technology_Node instances by a name match (precise, not contains), regardless of case
# Use this for getting instances that are expected to already be in the repository. Use theMatchString
# to specify the string to use as a match on existing instances. Matching is based on just the hostname
# and strips any trailing domain components from the name, after the first '.'
# If not found, create a new one.
# theClassName - the Essential class for the instance
# theExternalRef - the External Reference ID for this instance
# theExternalRepository - the External Repository that theExternalRef applies to
# theInstanceName - the name of the instance in the Essential Repository
# theMatchString - the string that should be used to match against and find the instance 
def getEssentialNodeInstanceIgnoreCase(theClassName, theExternalRef, theExternalRepository, theInstanceName, theMatchString):
	anInstList = kb.getCls(theClassName).getDirectInstances()
	for anInst in anInstList:
		anExternalRefList = anInst.getDirectOwnSlotValues(kb.getSlot("external_repository_instance_reference"))
		if anExternalRefList != None:	
			anExternalRef = getExternalRefInst(anExternalRefList, getExternalRepository(theExternalRepository))
			if anExternalRef != None:
				anExternalID = anExternalRef.getDirectOwnSlotValue(kb.getSlot("external_instance_reference"))
				if(anExternalID == theExternalRef):
					anExternalRef.setOwnSlotValue(kb.getSlot("external_update_date"), timestamp())
					print "Updated Instance via External Reference on class: " + theClassName
					return anInst
					
	# If we're here, this external reference hasn't been found.
	# Try to find by instance_name - ignoring case of each
	for anInst in anInstList:
		aName = anInst.getDirectOwnSlotValue(kb.getSlot("name"))
		if aName != None:
			aName = aName.split(".", 1)[0].lower()
			aMatchName = theMatchString.lower()
			if(aName == aMatchName):
				# We have found a match
				anExternalRef = createExternalRefInst(theExternalRepository, theExternalRef)
				anInst.addOwnSlotValue(kb.getSlot("external_repository_instance_reference"), anExternalRef)
				print "Updated instance via name match, on class: " + theClassName
				return anInst
				
	# if we're here, we haven't found one, so create one
	aNewInst = kb.createInstance(None, kb.getCls(theClassName))
	aNewInst.setOwnSlotValue(kb.getSlot("name"), theInstanceName)			
	anExternalRef = createExternalRefInst(theExternalRepository, theExternalRef)
	aNewInst.addOwnSlotValue(kb.getSlot("external_repository_instance_reference"), anExternalRef)
	print "Created new instance of class: " + theClassName
	return aNewInst
	
# Function to find instances by a name match (precise, not contains), regardless of case
# Use this for getting instances that are expected to already be in the repository. Use theMatchString
# to specify the string to use as a match on existing instances.
# If not found, create a new one.
# theClassName - the Essential class for the instance
# theExternalRef - the External Reference ID for this instance
# theExternalRepository - the External Repository that theExternalRef applies to
# theInstanceName - the name of the instance in the Essential Repository
# theMatchString - the string that should be used to match against and find the instance 
def getEssentialInstanceIgnoreCase(theClassName, theExternalRef, theExternalRepository, theInstanceName, theMatchString):
    anInstList = kb.getCls(theClassName).getDirectInstances()
    for anInst in anInstList:
        anExternalRefList = anInst.getDirectOwnSlotValues(kb.getSlot("external_repository_instance_reference"))
        if anExternalRefList != None:
            anExternalRef = getExternalRefInst(anExternalRefList, getExternalRepository(theExternalRepository))
            if anExternalRef != None:
                anExternalID = anExternalRef.getDirectOwnSlotValue(kb.getSlot("external_instance_reference"))
                if(anExternalID == theExternalRef):
                    anExternalRef.setOwnSlotValue(kb.getSlot("external_update_date"), timestamp())
                    print "Updated Instance via External Reference on class: " + theClassName
                    return anInst
					
    # If we're here, this external reference hasn't been found.
    # Try to find by instance_name - ignoring case of each
    aNameSlot = getNameSlotForClass(theClassName)
    for anInst in anInstList:
        aName = anInst.getDirectOwnSlotValue(kb.getSlot(aNameSlot))
        if aName != None:
            aName = aName.lower()
            aMatchName = theMatchString.lower()
            if(aName == aMatchName):
                # We have found a match
                anExternalRef = createExternalRefInst(theExternalRepository, theExternalRef)
                anInst.addOwnSlotValue(kb.getSlot("external_repository_instance_reference"), anExternalRef)
                print "Updated instance via name match, on class: " + theClassName
                return anInst
				
    # if we're here, we haven't found one, so create one
    aNewInst = kb.createInstance(None, kb.getCls(theClassName))
    aNewInst.setOwnSlotValue(kb.getSlot(aNameSlot), theInstanceName)			
    anExternalRef = createExternalRefInst(theExternalRepository, theExternalRef)
    aNewInst.addOwnSlotValue(kb.getSlot("external_repository_instance_reference"), anExternalRef)
    print "Created new instance of class: " + theClassName
    return aNewInst
	
# Find the right name slot for a given instance. If it's an EA_Class instance, the 
# name slot will be returned. If it's an EA_Relation instance, the relation_name slot
# is returned. If it's an instance of :EA_Graph_Relation, the :relation_name slot is
# returned
# theInstance the instance for which the correct name slot is required.
# returns a string name of the correct slot to use.
def getNameSlot(theInstance):
	aCorrectNameSlot = "name"
	for aSlot in theInstance.getOwnSlots():
		if(aSlot == kb.getSlot("name")):
			aCorrectNameSlot = "name"
		elif(aSlot == kb.getSlot("relation_name")):
			aCorrectNameSlot = "relation_name"
		elif(aSlot == kb.getSlot(":relation_name")):
			aCorrectNameSlot = ":relation_name"

	return aCorrectNameSlot
	
# Find the right name slot for a given class. If it's an EA_Class, the 
# name slot will be returned. If it's an EA_Relation class, the relation_name slot
# is returned. If it's an class of :EA_Graph_Relation, the :relation_name slot is
# returned
# theClassName the name of the class for which the correct name slot is required.
# returns a string name of the correct slot to use.
def getNameSlotForClass(theClassName):
	aCorrectNameSlot = "name"
	for aSlot in kb.getCls(theClassName).getTemplateSlots():
		if(aSlot == kb.getSlot("name")):
			aCorrectNameSlot = "name"
		elif(aSlot == kb.getSlot("relation_name")):
			aCorrectNameSlot = "relation_name"
		elif(aSlot == kb.getSlot(":relation_name")):
			aCorrectNameSlot = ":relation_name"

	return aCorrectNameSlot
	
#
def CreateNewEssentialInstance(theClassName, theInstanceName):
    """ Create a new instance in the repository without searching for any
        existing instances and without associating an external repository 
        reference
        
        theClassName - the name of the Class of which to create the instance
        theInstanceName - the value of the "name" slot on the new Essential instance
        
        returns a reference to the new instance
        
        19.11.2012 JWC
    """
    aNewInst = CreateNewEssentialInstanceWithID(theClassName, theInstanceName, None) 
    return aNewInst
    
#
def CreateNewEssentialInstanceWithID(theClassName, theInstanceName, theInstanceID):
    """ Create a new instance in the repository without searching for any
        existing instances and without associating an external repository 
        reference
        
        theClassName - the name of the Class of which to create the instance
        theInstanceName - the value of the "name" slot on the new Essential instance
        theInstanceID - the internal, Protege ID that should be used for this instance
        
        returns a reference to the new instance
        
        19.11.2012 JWC
    """
    # if we're here, we haven't found one, so create one
    aNewInst = kb.createInstance(theInstanceID, kb.getCls(theClassName))
	
    # Handle the 3 variants of name
    aNameSlot = getNameSlot(aNewInst)
    aNewInst.setOwnSlotValue(kb.getSlot(aNameSlot), theInstanceName)	
    print "Created new instance of class: " + theClassName
    return aNewInst

#
def GetEssentialInstanceByID(theClassName, theInstanceName, theInstanceID):
    """ Find the instance in the repository with the specified internal ID
        If not found, create one in the repository with that internal ID and with 
        the specified type and name.
        
        theClassName - the name of the Class of which to create the instance
        theInstanceName - the value of the "name" slot on the new Essential Instance
        theInstanceID - the internal, Protege ID that is being searched for and used
        for any new instance
        
        returns the new instance identified by ID
        
        19.11.2012 JWC
    """
    # Find an instance in the repository with internal ID = theInstanceID
    anInstance = kb.getInstance(theInstanceID)
    if anInstance != None:
        print "Found instance by ID on class: " + theClassName
         
    # If not found, create it
    if anInstance == None:
        anInstance = CreateNewEssentialInstanceWithID(theClassName, theInstanceName, theInstanceID)
    
    return anInstance
#

# Intelligent Essential Get Instance function.
def EssentialGetInstance(theClassName, theInstanceID, theInstanceName, theExternalID, theExternalRepositoryName):
    """ Get the Essential instance from the current repository of the specified Class. 
        Firstly, the repository will be searched for the specified instance ID (internal Protege name). 
        If no such instance can be found, the repository is searched for an instance with the specified external 
        repository instance reference. 
        If no such instance can be found, the repository is searched is for instances of the Specified class that
        has a name that exactly (case and full name) matches the specified instance name.
        If no such instance can be found, a new instance with the above the parameters is created. In this case
        Protege will automatically assign a new instance ID.
        
        theClassName - the name of the class of the instance to find. Search is scoped by class
        theInstanceID - the internal Protege name / ID for the instance. Set to "" to bypass search by instance ID
        theInstanceName - the name of the specified instance. When an instance is found by instance ID or External
                          reference, this parameter can be used to update the name (Essential name slot) of the 
                          instance.
        theExternalID - the ID that the instance has in the specified external source repository
        theExternalRepositoryName - the name of the external source repository         
        
        returns a reference to the correct Essential Instance or None if an attempt is made to create an instance
        of an unknown class.
        
        20.11.2012 JWC
    """
    anEssentialInstance = None
    
    # 20.09.2011 JWC - Make sure that the source class is in the targert repository
    aClass = kb.getCls(theClassName)    
    # if not-report a warning and skip that instance.
    if aClass == None:
        print "WARNING: Skipping instance of unknown class: " + theClassName
        return None
    
    if theInstanceID != None:
        anEssentialInstance = FindEssentialInstanceByID(theInstanceID)        
        ProcessFoundInstance(anEssentialInstance, theInstanceName, theExternalRepositoryName, theExternalID)
        if anEssentialInstance != None:
            print "Updated instance via instance ID, on class: " + theClassName
            
    # If not found, search by external repository reference
    if anEssentialInstance == None:
        anEssentialInstance = FindEssentialInstanceByExternalRef(aClass, theExternalRepositoryName, theExternalID)
        ProcessFoundInstance(anEssentialInstance, theInstanceName, theExternalRepositoryName, theExternalID)
        if anEssentialInstance != None:
            print "Updated instance via external repository reference, on class: " + theClassName
        
        # If not found, search by name
        if anEssentialInstance == None:
            anEssentialInstance = FindEssentialInstanceByName(aClass, theInstanceName)
            UpdateOrAddExternalRef(anEssentialInstance, theExternalRepositoryName, theExternalID)
            if anEssentialInstance != None:
                print "Updated instance via name, on class: " + theClassName
        
        # If not found, create a new instance
        if anEssentialInstance == None:            
            anEssentialInstance = CreateNewEssentialInstance(theClassName, theInstanceName)
            AddExternalReferenceID(anEssentialInstance, theExternalID, theExternalRepositoryName)
    
    # Return the results of the searches.            
    return anEssentialInstance
#

def FindEssentialInstanceByID(theInstanceID):
    """ Find the instance of the specified class that has the internal ID specified.
        If not found returns None
        
        theClass - the class of the instance to find
        theInstanceID - the internal, Protege name of the instance
     
        returns a reference to the found instance or None if not found
        
        20.11.2012 JWC
    """
    anInstance = None
    if theInstanceID != None and len(theInstanceID) > 0:
        anInstance = kb.getInstance(theInstanceID)
        
    return anInstance
#

def FindEssentialInstanceByExternalRef(theClass, theExternalRepositoryName, theExternalID):
    """ Find the Essential instance of the specified class in the repository, that has
        the specified external reference.
        
        theClass - the class of the required instance
        theExternalRepositoryName - the external repository name that contains the external ID
        theExternalID - the ID of the required instance in the specified external source repository
        
        returns a reference to the found instance or None if not found
        20.11.2012 JWC
    """
    anInstance = None
    anExternalRepos = getExternalRepository(theExternalRepositoryName)
    if anExternalRepos != None:
        anInstList = theClass.getDirectInstances()
        for anInst in anInstList:
            anExternalRef = FindExternalReferenceID(anInst, theExternalID, theExternalRepositoryName)
            if anExternalRef != None:
                UpdateExternalReferenceID(anExternalRef)                                    
                anInstance = anInst
                break
                
    return anInstance
    
#
def FindEssentialInstanceByName(theClass, theInstanceName):
    """ Find the Essential instance of the specified class in the repository that has
        a name that exactly matches the specified name
        
        theClass - the class of the required instance
        theInstance - the name of the instance to find
        
        returns a reference to the found instance or None if not found
        
        20.11.2012 JWC
    """
    anInstance = None 
    if theInstanceName != None:
        aSearchName = theInstanceName.strip()
        aNameSlotName = getNameSlotForClass(theClass.getName())
        aNameSlot = kb.getSlot(aNameSlotName)
        
        anInstList = theClass.getDirectInstances()
        for anInst in anInstList:
            anInstName = anInst.getDirectOwnSlotValue(aNameSlot)
            if anInstName == aSearchName:
                anInstance = anInst
                break
    
    return anInstance
#
def AddExternalReferenceID(theInstance, theExternalID, theExternalRepository):
    """ Add the specified external repository instance reference to the specified instance
    
        theInstance - the Protege instance to which the external reference should be created and added
        theExternalID - the ID from the external repository for the specified instance
        theExternalRepository - the external repository to which the external ID belongs
        
        20.11.2012 JWC
    """
    anExternalRef = createExternalRefInst(theExternalRepository, theExternalID)
    theInstance.addOwnSlotValue(kb.getSlot("external_repository_instance_reference"), anExternalRef)
#
#
def FindExternalReferenceID(theInstance, theExternalID, theExternalRepositoryName):
    """ Find the specified external reference for the Instance with the specified external ID on the
        specified external repository or return None
    
        theInstance - the instance to which the external ID relates
        theExternalID - the ID of this instance in the external repository
        theExternalRepositoryName - the external source repository from which the instance is being imported
    
        returns a reference the external repository object or None if not found.
        
        21.11.2012 JWC
    """
    anExternalRef = None
    anExternalRepos = getExternalRepository(theExternalRepositoryName)
    
    anExternalRefList = theInstance.getDirectOwnSlotValues(kb.getSlot("external_repository_instance_reference"))
    for aRef in anExternalRefList:
        aRepos = aRef.getDirectOwnSlotValue(kb.getSlot("external_repository_reference"))
        if aRepos == anExternalRepos:
            # Check the ID matches
            aRefName = aRef.getDirectOwnSlotValue(kb.getSlot("external_instance_reference"))
            if aRefName == theExternalID:
                anExternalRef = aRef
                break
    
    return anExternalRef
            
#
def UpdateExternalReferenceID(theExternalRepositoryRef):
    """ Update the timestamp on the specified external repository reference
    
        theExternalRepositoryRef - the external repository reference to update.
        
        21.11.2012 JWC
    """
    theExternalRepositoryRef.setOwnSlotValue(kb.getSlot("external_update_date"), timestamp())
    
#
def UpdateEssentialInstanceName(theInstance, theInstanceName):
    """ Update the name of the specified instance to use the new name specified
        but only if the names do not match
        
        theInstance - the instance to be updated
        theInstanceName - the new name to use
        
        21.11.2012 JWC
    """
    if theInstance != None:
        if (theInstanceName != None) and (len(theInstanceName) > 0):
            theInstance.setOwnSlotValue(kb.getSlot("name"), theInstanceName)
#

def UpdateOrAddExternalRef(theInstance, theExternalRepositoryName, theExternalID):
    """ Find the correct External reference for the specified instance in the specified
        repository with the specified ID and update it. If no such external instance reference
        exists, create it
        
        theInstance - the instance for which the external reference should be updated or added
        theExternalRepositoryName - the name of the external repository
        theExternalID - the external ID in the external repository for the instance
        
        21.11.2012 JWC
    """
    if theInstance != None:
        anExternalReposRef = FindExternalReferenceID(theInstance, theExternalID, theExternalRepositoryName)
        if anExternalReposRef != None:            
            UpdateExternalReferenceID(anExternalReposRef)
        else:
            AddExternalReferenceID(theInstance, theExternalID, theExternalRepositoryName)
#

def ProcessFoundInstance(theInstance, theInstanceName, theExternalRepositoryName, theExternalID):
    """ Process an Essential instance that has been found by updating the relevant external repository instance
        reference. If theInstanceName contains a non-empty value, change the Essential name slot value
        for theInstance
        
        theInstance - the Essential instance to process
        theInstanceName - the new/updated name for the instance. Sets the Essential Meta Model name slot
        theExternalRepositoryName - the name of the external source repository
        theExternalID - the ID that the specified instance has in the external source repository
        
        21.11.2012 JWC       
    """
    if theInstance != None:
        # Update the external reference instance for the instance
        UpdateOrAddExternalRef(theInstance, theExternalRepositoryName, theExternalID)
        
        # If theInstanceName is populated (not None or "") change the name of theInstance
        if (theInstanceName != None) and (len(theInstanceName) > 0):
            UpdateEssentialInstanceName(theInstance, theInstanceName)
#
# Get an existing or new Actor To Role relation for the specified Actor and Role
def GetActorToRole(theActor, theRole, theExtRepos):
    """ Get an existing or new Actor To Role relation for the specified Actor and Role
    
        theActor - the Actor instance to add to the role
        theRole - the Role that the Actor is to play
        theExtRepos - the name of the External repository from which the actors and roles are being
                      imported.
    
        returns the relevant ActorToRole relation or None if Actor or Role is invalid
    """
    anActToRole = None
    if (theActor != None) and (theRole != None):
        anActorName = theActor.getOwnSlotValue(kb.getSlot("name"))
        aRoleName = theRole.getOwnSlotValue(kb.getSlot("name"))
        anActToRoleName = anActorName + "::as::" + aRoleName
        anActToRole = EssentialGetInstance("ACTOR_TO_ROLE_RELATION", "", anActToRoleName, anActToRoleName, theExtRepos)
        addIfNotThere(anActToRole, "act_to_role_from_actor", theActor)        
        addIfNotThere(anActToRole, "act_to_role_to_role", theRole)
            
    return anActToRole
#