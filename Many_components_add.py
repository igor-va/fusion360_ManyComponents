#Author-IA
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)

# Command inputs
_numСomp = adsk.core.StringValueCommandInput.cast(None)

_handlers = []

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Create a command definition and add a button to the CREATE panel.
        cmdDef = _ui.commandDefinitions.addButtonDefinition('adskManyCompPythonAddIn', 'Many Components', 'Create any number of components', 'Resources/ManyComp')        
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        manyCompButton = createPanel.controls.addCommand(cmdDef, 'FusionCreateNewComponentCommand', False)
        
        # Connect to the command created event.
        onCommandCreated = ManyCompCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        if context['IsApplicationStartup'] == False:
            _ui.messageBox('The "Many Components" command has been added\nto the CREATE panel of the MODEL workspace.')
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        manyCompButton = createPanel.controls.itemById('adskManyCompPythonAddIn')       
        if manyCompButton:
            manyCompButton.deleteMe()
        
        cmdDef = _ui.commandDefinitions.itemById('adskManyCompPythonAddIn')
        if cmdDef:
            cmdDef.deleteMe()
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
            
# Event handler for the commandCreated event.
class ManyCompCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            
            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()

            numComp = '2'            
            numСompAttrib = des.attributes.itemByName('ManyComp', 'numComp')
            if numСompAttrib:
                numComp = numСompAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            
            global _numComp

            # Define the command dialog.                                   
            _numComp = inputs.addStringValueInput('numComp', 'Number of Components', numComp)        
            
            # Connect to the command related events.
            onExecute = ManyCompCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute) 
            
            onValidateInputs = ManyCompCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs) 
                   
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

               
# Event handler for the execute event.
class ManyCompCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:            
            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            attribs.add('ManyComp', 'numСomp', str(_numComp.value))

            # Get the current values.
            numComp = int(_numComp.value)

            # Create the many components.
            manyComp = createManyComp(des, numComp)
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                
# Event handler for the validateInputs event.
class ManyCompCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            
            # Verify that at lesat 4 teath are specified.
            if not _numComp.value.isdigit():
                eventArgs.areInputsValid = False
                return
            else:    
                numComp = int(_numComp.value)
            
            if numComp < 1:
                eventArgs.areInputsValid = False
                return
                           
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

               
# Create Many Components.
def createManyComp(design, numComp):
    try:
        # Get the root component of the active design
        rootComp = design.rootComponent

        allOccs = rootComp.occurrences
        transform = adsk.core.Matrix3D.create()

        components = []

        # Create a component under root component
        for occ in range(numComp):
            occ = allOccs.addNewComponent(transform)                 
            subComp = occ.component
            components.append(subComp)      
            
        return components
        
    except Exception as error:
        _ui.messageBox("ManyComp Failed : " + str(error)) 
        return None                
