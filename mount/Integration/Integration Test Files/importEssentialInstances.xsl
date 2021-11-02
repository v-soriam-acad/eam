<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
    xmlns:pro="http://protege.stanford.edu/xml"
    xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xsl:character-map name="special_chars">
        <xsl:output-character character="&#8482;" string="\u2122"/>
    </xsl:character-map>
    <xsl:output media-type="text-plain" method="text" omit-xml-declaration="yes" use-character-maps="special_chars" encoding="UTF-8"></xsl:output>
    <xsl:param name="ExternalRepository"></xsl:param>
    <xsl:param name="ExternalRepositoryDesc"></xsl:param>
    <!-- 
        * Copyright (c)2009-2013 Enterprise Architecture Solutions ltd.
        * This file is part of Essential Architecture Manager, 
        * the Essential Architecture Meta Model and The Essential Project.
        *
        * Essential Architecture Manager is free software: you can redistribute it and/or modify
        * it under the terms of the GNU General Public License as published by
        * the Free Software Foundation, either version 3 of the License, or
        * (at your option) any later version.
        *
        * Essential Architecture Manager is distributed in the hope that it will be useful,
        * but WITHOUT ANY WARRANTY; without even the implied warranty of
        * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        * GNU General Public License for more details.
        *
        * You should have received a copy of the GNU General Public License
        * along with Essential Architecture Manager.  If not, see <http://www.gnu.org/licenses/>.
        * 
       
        Generic instance importing solution for importing instances from an Essential Architecture
        Manager repository into another one.
        You can use the InstanceSlot template in this file to import all the slot entries for an instance
        that are Instance Slots. See the documentation above the template for requirements and details.
        
        17.03.2009    JWC    First version
        17.03.2009    JWC    Completed generic import solution
        20.03.2009    JWC    Fixed to correctly name EA_Relation and EA_Graph_Relation instances
        31.03.2009    JWC    Added statement to define the specified External Repository
        28.04.2009    JWC    Can now handle duplicates in source elegantly and non-string slot values
        29.04.2009    JWC    Added reporting of duplicate instances with mis-matching types
        24.12.2009	  JWC    Added the includepath variable to bring in standard functions for use with 
        					 the Essential Integration Tab
        22.08.2010    JWC    Fixed bugs with Instance slots, Float slots and strings that contain '"' characters.
        20.09.2011    JWC    Fixed issue importing unknown classes, started character map for special characters.
        27.09.2011    JWC    Revised handling of Boolean slots
        03.10.2011    JWC    Handle multiple values for strings
        04.10.2011    JWC    Cater for slots in source that don't exist in target project.
        31.10.2011    JWC    Moved guard code to Standard Functions and handle large number of instances in an
                             instance slot.
        30.01.2013    JWC    v2.0 Re-implemented to handle UTF-8 encoded / Unicode characters
    -->
    
    <!-- Process all simple instances in the source XML -->
    <xsl:template match="pro:knowledge_base">
        <xsl:text># -*- coding: UTF-8 -*- &#xa;</xsl:text>
        <xsl:text># (c)2009-2013 Enterprise Architecture Solutions ltd - Essential Architecture Manager instance import script &#xa;</xsl:text>
        <xsl:text># created: </xsl:text><xsl:value-of select="current-dateTime()"></xsl:value-of><xsl:text>&#xa;</xsl:text>
        <xsl:text>import java&#xa;&#xa;</xsl:text>
        <xsl:text>from java.lang import Boolean&#xa;&#xa;</xsl:text>
        <xsl:text>from java.lang import Float&#xa;&#xa;</xsl:text>
        <xsl:text>standardFunctionsFile = includepath + "/standardFunctions.py"&#xa;</xsl:text>
        <xsl:text>execfile(standardFunctionsFile)&#xa;&#xa;</xsl:text>
        <xsl:text># instance update and creation code follows&#xa;</xsl:text>
        <xsl:text>#&#xa;</xsl:text>
        <xsl:text>&#xa;</xsl:text>
        <!-- Setup the external repository if it is not already defined in the Essential repository -->
        <!-- This only needs to be called once, so make sure that we only create it if it's not there -->
        <xsl:text># Define the external source repository - does nothing if already defined.&#xa;</xsl:text>       
        <xsl:text>defineExternalRepository("</xsl:text><xsl:value-of select="$ExternalRepository"></xsl:value-of>
        <xsl:text>", "</xsl:text><xsl:value-of select="$ExternalRepositoryDesc"></xsl:value-of><xsl:text>")&#xa;&#xa;</xsl:text>
        
        <!-- 20.09.2011 JWC exclude the About_Essential instances -->
        <xsl:apply-templates select="/node()/pro:simple_instance[(pro:type != 'Essential_Licensing') and (pro:type !='Meta_Model_Version') and (pro:type != 'Applied_Updates')]" mode="ImportSimpleInstance"></xsl:apply-templates>
    </xsl:template>
    
    <!-- 
        ImportSimpleInstance.
        Requires the ExternalRepository parameter to be set and imports instances from the source 
        repository and builds the script to import it into the target.
        If any class refactoring is required, define the exceptions, e.g. replace 'Actor' instances
        with 'Individual_Instances', code these into the GetInstanceClass template.
        The Essential Integration Server chunking is supported by this template, which writes the 
        #####_End_of_Node_#### marker after each new instance.
        Extend this to make the generic instance importer. Use the GetInstanceClass on this to get the class
        of the simple instance. Add additional steps to handle the other slot types
    -->
    <xsl:template match="node()" mode="ImportSimpleInstance">
        <!-- Check for duplicate instance IDs -->      
        <xsl:apply-templates select="pro:name" mode="CheckForDuplicateInstances"></xsl:apply-templates>
        
        <xsl:text>theInstance = getEssentialInstanceContains("</xsl:text><xsl:apply-templates select="pro:name" mode="GetInstanceClass"></xsl:apply-templates><xsl:text>", "</xsl:text>
        <xsl:value-of select="pro:name"></xsl:value-of>
        <xsl:text>", "</xsl:text><xsl:value-of select="$ExternalRepository"></xsl:value-of><xsl:text>", </xsl:text>
            <xsl:call-template name="RenderUnicode">
                <xsl:with-param name="sourceString">
                    <!-- Get the Essential name of the instance. Use either the name, relation_name or :relation_name -->
                    <xsl:value-of select="pro:own_slot_value[pro:slot_reference='name']/pro:value"></xsl:value-of>
                    <xsl:value-of select="pro:own_slot_value[pro:slot_reference='relation_name']/pro:value"></xsl:value-of>
                    <xsl:value-of select="pro:own_slot_value[pro:slot_reference=':relation_name']/pro:value"></xsl:value-of>
                </xsl:with-param>
            </xsl:call-template>
        <xsl:text>)&#xa;</xsl:text>
        
        <!-- Handle NULL instances - e.g. unknown Class 
        <xsl:if test="count(pro:own_slot_value) > 0">
            <xsl:text>if theInstance != None:&#xa;</xsl:text>
        </xsl:if> -->
        <!-- Instance Slots -->
        <xsl:apply-templates select="pro:own_slot_value[pro:value/@value_type='simple_instance']" mode="InstanceSlot"></xsl:apply-templates>
        
        <!-- String Slots -->
        <xsl:apply-templates select="pro:own_slot_value[pro:value/@value_type='string']" mode="StringSlot"></xsl:apply-templates>
        
        <!-- Integer Slots -->
        <xsl:apply-templates select="pro:own_slot_value[pro:value/@value_type='integer']" mode="IntegerSlot"></xsl:apply-templates>
        
        <!-- Float Slots -->
        <xsl:apply-templates select="pro:own_slot_value[pro:value/@value_type='float']" mode="FloatSlot"></xsl:apply-templates>
        
        <!-- Boolean Slots -->
        <xsl:apply-templates select="pro:own_slot_value[pro:value/@value_type='boolean']" mode="BooleanSlot"></xsl:apply-templates>
        
        <xsl:text>&#xa;####_End_of_Node_####&#xa;&#xa;</xsl:text>
    </xsl:template>
    
    <!-- Send this template a set of one or more nodes of <own_slot_value> tags that have a value_type of simple_instance
        That is, a slot that is of type Instance Slot. Use a select statement such as: 
        select="pro:own_slot_value[pro:value/@value_type='simple_instance']" mode="InstanceSlot"
        from a simple instance node.
        This template then finds or creates the instances that need to be added to the specified slot.
        The template assumes that somewhere above, the 'standardFunctions.py' Jython library will have been executed.
        Additionally, the template REQUIRES that you set a variable: 'theInstance' to the value of your new instance
        that contains these slot values.
    -->
    <xsl:template match="node()" mode="InstanceSlot">
        <!-- Take a node which is the entry for the instance attribute - this could have multiple values -->
        <!-- Get the slot that the instances will go in-->
        <xsl:text>aSlotName = "</xsl:text><xsl:value-of select="pro:slot_reference"></xsl:value-of><xsl:text>"</xsl:text>
        <xsl:text>&#xa;</xsl:text>
        <xsl:for-each select="pro:value">
            <xsl:text>anInstanceSlot = getEssentialInstanceContains("</xsl:text><xsl:apply-templates select="." mode="GetInstanceClass"></xsl:apply-templates><xsl:text>", "</xsl:text>
            <xsl:value-of select="."></xsl:value-of>
            <xsl:text>", "</xsl:text><xsl:value-of select="$ExternalRepository"></xsl:value-of><xsl:text>", </xsl:text>
            <xsl:apply-templates select="." mode="GetInstanceName"></xsl:apply-templates>
            <xsl:text>)&#xa;</xsl:text>
            
            <!-- Handle empty instances that might have been returned -->
            <xsl:text>if anInstanceSlot != None:&#xa;</xsl:text>
            <!-- Handle multi/single cardinality instance slots -->
            <xsl:text>    addIfNotThere(theInstance, aSlotName, anInstanceSlot)</xsl:text>
            <!-- Chunk here after slot setting to handle large numbers of slot values -->
            <xsl:text>&#xa;####_End_of_Node_####&#xa;</xsl:text>
            <xsl:text>&#xa;</xsl:text>            
        </xsl:for-each>
    </xsl:template>
    
    <!-- Find the instance name from the id -->
    <xsl:template match="node()" mode="GetInstanceName">
        <xsl:variable name="anID" select="node()"></xsl:variable>
        <xsl:variable name="anInstance" select="/node()/pro:simple_instance[pro:name=$anID]"></xsl:variable>
        
        <!-- Get the Essential name of the instance. Use either the name, relation_name or :relation_name -->
        <xsl:call-template name="RenderUnicode">
            <xsl:with-param name="sourceString">
                <!-- Get the Essential name of the instance. Use either the name, relation_name or :relation_name -->
                <xsl:value-of select="$anInstance/pro:own_slot_value[pro:slot_reference='name']/pro:value"></xsl:value-of>
                <xsl:value-of select="$anInstance/pro:own_slot_value[pro:slot_reference='relation_name']/pro:value"></xsl:value-of>
                <xsl:value-of select="$anInstance/pro:own_slot_value[pro:slot_reference=':relation_name']/pro:value"></xsl:value-of>
            </xsl:with-param>
        </xsl:call-template>
        
    </xsl:template>
    
    <!-- Find the class of an instance from its ID -->
    <xsl:template match="node()" mode="GetInstanceClass">
        <xsl:variable name="anID" select="node()"></xsl:variable>
        <xsl:variable name="anInstance" select="/node()/pro:simple_instance[pro:name=$anID]"></xsl:variable>
        <!-- Handle duplicate instance IDs and with different Instance types -->
        <xsl:variable name="aSourceClass" select="distinct-values($anInstance/pro:type)[1]"></xsl:variable>
        
        <!-- To do the Class mapping, we add exceptions in here - replacing the line above
            e.g. set the xsl:value-of to a variable, then perform an xsl:choose on it e.g.
            xsl:when select="$aClass = 'Actor'" xsl:value-of 'Individual_Actor'
            xsl:otherwise xsl:value-of $aClass -->
        <xsl:choose>
            <xsl:when test="$aSourceClass = 'Actor'"><xsl:value-of>Group_Actor</xsl:value-of></xsl:when>
            <xsl:when test="$aSourceClass = 'Business_Role'"><xsl:value-of>Group_Business_Role</xsl:value-of></xsl:when>
            <xsl:otherwise><xsl:value-of select="$aSourceClass"></xsl:value-of></xsl:otherwise>
        </xsl:choose>
        
    </xsl:template>
    
    <!-- Import String slots -->
    <!-- Updated 03.10.2011 / 04.10.2011 JWC -->
    <!-- Re-implemented for Unicode / UTF-8 30.01.2013 JWC -->
    <xsl:template match="node()" mode="StringSlot">
        <!-- Drop the eas_version slot -->
        <xsl:variable name="slotName" select="pro:slot_reference"></xsl:variable>
        <xsl:choose>
            <xsl:when test="($slotName != 'eas_version') and ($slotName != 'eas_relation_version') and ($slotName != ':eas_relation_version')">
                <xsl:text>aSlotName = "</xsl:text><xsl:value-of select="pro:slot_reference"></xsl:value-of><xsl:text>"</xsl:text>
                <xsl:text>&#xa;</xsl:text>
                <xsl:choose>
                    <xsl:when test="count(pro:value) > 1">
                        <!-- Multiple string values -->
                        <xsl:for-each select="pro:value">
                            <xsl:variable name="aValue" select="."></xsl:variable>
                            
                            <!-- 03.10.2011 JWC, handle multi-strings -->
                            <!-- Only add a string if it's not already there -->
                            <xsl:text>addIfNotThere(theInstance, aSlotName, </xsl:text>
                                <!--<xsl:value-of select="$aSlotValueDeQuoted"></xsl:value-of>-->
                                <xsl:call-template name="RenderUnicode">
                                    <xsl:with-param name="sourceString" select="$aValue"></xsl:with-param>
                                </xsl:call-template>
                            <xsl:text>)</xsl:text>
                            <xsl:text>&#xa;</xsl:text>
                        </xsl:for-each>
                    </xsl:when>
                    <xsl:otherwise>
                        <!-- Single String value -->
                        <xsl:variable name="aSlotValue" select="pro:value"></xsl:variable>
                        <xsl:text>setSlot(theInstance, aSlotName, </xsl:text>
                            <!--<xsl:value-of select="$aSlotValueDeQuoted"></xsl:value-of>-->
                            <xsl:call-template name="RenderUnicode">
                                <xsl:with-param name="sourceString" select="$aSlotValue"></xsl:with-param>
                            </xsl:call-template>
                        <xsl:text>)</xsl:text>
                        <xsl:text>&#xa;</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
        </xsl:choose>
        
    </xsl:template>
    
    <!-- Import Integer slots -->
    <!-- 04.10.2011 JWC - cater for slots in source not in target project -->
    <xsl:template match="node()" mode="IntegerSlot">
        <!-- Drop the eas_version slot -->
        <xsl:variable name="slotName" select="pro:slot_reference"></xsl:variable>
        <xsl:choose>
            <xsl:when test="($slotName != 'eas_version') and ($slotName != 'eas_relation_version') and ($slotName != ':eas_relation_version')">
                <xsl:text>aSlotName = "</xsl:text><xsl:value-of select="pro:slot_reference"></xsl:value-of><xsl:text>"</xsl:text>
                <xsl:text>&#xa;</xsl:text>
                <xsl:variable name="aSlotValue" select="replace(pro:value, '&#xa;', ' ')"></xsl:variable>
                <xsl:text>setSlot(theInstance, aSlotName, </xsl:text><xsl:value-of select="$aSlotValue"></xsl:value-of><xsl:text>)</xsl:text>
                <xsl:text>&#xa;</xsl:text>
            </xsl:when>
        </xsl:choose>
        
    </xsl:template>
    
    <!-- Import Float slots -->
    <!-- 04.10.2011 JWC - cater for slots in source not in target project -->
    <xsl:template match="node()" mode="FloatSlot">
        <!-- Drop the eas_version slot -->
        <xsl:variable name="slotName" select="pro:slot_reference"></xsl:variable>
        <xsl:choose>
            <xsl:when test="($slotName != 'eas_version') and ($slotName != 'eas_relation_version') and ($slotName != ':eas_relation_version')">
                <xsl:text>aSlotName = "</xsl:text><xsl:value-of select="pro:slot_reference"></xsl:value-of><xsl:text>"</xsl:text>
                <xsl:text>&#xa;</xsl:text>
                <xsl:variable name="aSlotValue" select="replace(pro:value, '&#xa;', ' ')"></xsl:variable>
                
                <!-- 22.8.2010 JWC Resolve float slot value setting problem -->
                <!-- 04.10.2011 JWC handle bad slots -->
                <xsl:text>aSlot = kb.getSlot(aSlotName)</xsl:text>
                <xsl:text>&#xa;</xsl:text>
                <xsl:text>if (theInstance != None) and (aSlot != None):</xsl:text>
                <xsl:text>&#xa;</xsl:text>                
                <xsl:text>    theInstance.setOwnSlotValue(aSlot, Float(&quot;</xsl:text><xsl:value-of select="$aSlotValue"></xsl:value-of><xsl:text>&quot;))</xsl:text>
                <xsl:text>&#xa;</xsl:text>                
            </xsl:when>
        </xsl:choose>
        
    </xsl:template>
    
    <!-- Import Boolean slots -->
    <!-- 04.10.2011 JWC - cater for slots in source not in target project -->    
    <xsl:template match="node()" mode="BooleanSlot">
        <!-- Drop the eas_version slot -->
        <xsl:variable name="slotName" select="pro:slot_reference"></xsl:variable>
        <xsl:choose>
            <xsl:when test="($slotName != 'eas_version') and ($slotName != 'eas_relation_version') and ($slotName != ':eas_relation_version')">
                <xsl:text>aSlotName = "</xsl:text><xsl:value-of select="pro:slot_reference"></xsl:value-of><xsl:text>"</xsl:text>
                <xsl:text>&#xa;</xsl:text>
                <xsl:variable name="aSlotValue" select="replace(pro:value, '&#xa;', ' ')"></xsl:variable>
                
                <!-- 27.09.2011 JWC Resolve boolean slot value setting problem -->
                <!-- 04.10.2011 JWC handle bad slots -->
                <xsl:text>aSlot = kb.getSlot(aSlotName)</xsl:text>
                <xsl:text>&#xa;</xsl:text>
                <xsl:text>if (theInstance != None) and (aSlot != None):</xsl:text>
                <xsl:text>&#xa;</xsl:text>                
                <xsl:text>    theInstance.setOwnSlotValue(aSlot, Boolean(&quot;</xsl:text><xsl:value-of select="$aSlotValue"></xsl:value-of><xsl:text>&quot;))</xsl:text>
                <xsl:text>&#xa;</xsl:text>
            </xsl:when>
        </xsl:choose>
        
    </xsl:template>
    
    <!-- Check for duplicate instance IDs, i.e. /simple_instance/name
    not unique. This is not allowed but can happen. The import service manages duplicate instance IDs as
    long as the /simple_instance/type is consistent across duplicates. Mis-matched types only use the first 'type'
    encountered BUT this template generates an error report message -->
    <xsl:template match="node()" mode="CheckForDuplicateInstances">
        <xsl:variable name="anID" select="node()"></xsl:variable>
        <xsl:variable name="anInstance" select="/node()/pro:simple_instance[pro:name=$anID]"></xsl:variable>
        
        <xsl:if test="count(distinct-values($anInstance/pro:type)) > 1">
            <xsl:text>&#xa;</xsl:text>
            <xsl:text>print "*** DUPLICATE INSTANCE ID with mis-matched TYPE definition for instance: </xsl:text><xsl:value-of select="$anID"></xsl:value-of>
            <xsl:text>. Types specified: </xsl:text><xsl:value-of select="distinct-values($anInstance/pro:type)"></xsl:value-of>
            <xsl:text>"&#xa;</xsl:text>
            <xsl:text>print "*** Using type: </xsl:text><xsl:value-of select="distinct-values($anInstance/pro:type)[1]"></xsl:value-of>
            <xsl:text>"&#xa;</xsl:text>
        </xsl:if>
    </xsl:template>
    
    <!-- 
        Template to render any string as a safe set of Unicode characters, ready 
        for use by the Python script. Note that this template includes the " characters
        to delimit the string as the Python unicode format requires a 'u' prefix.
        Pass any source string in to the parameter sourceString.
        
        30.01.2013 JWC
    -->
    <xsl:template name="RenderUnicode">
        <xsl:param name="sourceString"></xsl:param>
        <!-- Get the set of unicode codepoints for the string -->
        <xsl:variable name="codes" select="string-to-codepoints($sourceString)"></xsl:variable>
        <!-- Build the Python Unicode string -->
        <xsl:text>u"</xsl:text>
        
        <xsl:for-each select="$codes">
            <xsl:variable name="aNumber">
                <xsl:call-template name="ConvertDecToHex">
                    <xsl:with-param name="index" select="current()"></xsl:with-param>
                </xsl:call-template>
            </xsl:variable>
            <xsl:text>\u</xsl:text>
                <!-- Python needs unicode in 4-digit format -->
                <xsl:value-of select="concat(substring('0000', 1, 4 - string-length($aNumber)), $aNumber)"/>                
        </xsl:for-each>
        <xsl:text>"</xsl:text>
    </xsl:template>
    
    <!-- 
       Convert a given decimal value in the parameter 'index' 
       to hexidecimal value.

       30.01.2013 JWC
    -->
    <xsl:template name="ConvertDecToHex">
        <xsl:param name="index" />
        <xsl:if test="$index > 0">
            <xsl:call-template name="ConvertDecToHex">
                <xsl:with-param name="index" select="floor($index div 16)" />
            </xsl:call-template>
            <xsl:choose>
                <xsl:when test="$index mod 16 &lt; 10">
                    <xsl:value-of select="$index mod 16" />
                </xsl:when>
                <xsl:otherwise>
                    <xsl:choose>
                        <xsl:when test="$index mod 16 = 10">A</xsl:when>
                        <xsl:when test="$index mod 16 = 11">B</xsl:when>
                        <xsl:when test="$index mod 16 = 12">C</xsl:when>
                        <xsl:when test="$index mod 16 = 13">D</xsl:when>
                        <xsl:when test="$index mod 16 = 14">E</xsl:when>
                        <xsl:when test="$index mod 16 = 15">F</xsl:when>
                        <xsl:otherwise>A</xsl:otherwise>
                    </xsl:choose>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:if>
    </xsl:template>
    
</xsl:stylesheet>
