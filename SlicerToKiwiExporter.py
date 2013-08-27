import json
import os
import zipfile
import contextlib
import datetime
import vtk, slicer

#
# SlicerToKiwiExporter
#

class SlicerToKiwiExporter:
  def __init__(self, parent):
    parent.title = "Slicer to KiwiViewer exporter"
    parent.categories = ["Exporter"]
    parent.dependencies = []
    parent.contributors = ["Jean-Christophe Fillion-Robin (Kitware), Pat Marion (Kitware), Steve Pieper (Isomics)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc.  and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
    parent.hidden = True
    self.parent = parent

#
# SlicerToKiwiExporterFileWriter
#

class SlicerToKiwiExporterFileWriter:
    def __init__(self, parent):
        self.parent = parent
    
    def description(self):
        return 'KiwiViewer File'
    
    def fileType(self):
        return 'SceneFile'
    
    def canWriteObject(self, obj):
        return isinstance(obj, slicer.vtkMRMLScene)
    
    def extensions(self, obj):
        return ['KiwiViewer File (*.kiwi.zip)']
    
    def write(self, properties):
        self.exportModels(properties['fileName'])
        return True

    def exportModel(self, model, outDir):
        
        modelDisplay = model.GetDisplayNode()
        if not modelDisplay or not modelDisplay.GetVisibility():
            return None
        
        print('  exporting %s' % model.GetName())
        
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetInput(model.GetPolyData())
        fileName = os.path.join(outDir, model.GetName() + '.vtp')
        writer.SetFileName(fileName)
        writer.Write()

        data = {}
        data['name'] = model.GetName()
        data['color'] = modelDisplay.GetColor()
        data['opacity'] = modelDisplay.GetOpacity()
        data['filename'] = fileName
        
        representation = modelDisplay.GetRepresentation()
        if representation == slicer.vtkMRMLDisplayNode.WireframeRepresentation:
            data['geometry_mode'] = 'wireframe'
        elif representation == slicer.vtkMRMLDisplayNode.SurfaceRepresentation \
          and modelDisplay.GetEdgeVisibility():
            data['geometry_mode'] = 'surface_with_edges'
        elif representation == slicer.vtkMRMLDisplayNode.PointsRepresentation:
            data['geometry_mode'] = 'points'

        return data
        
    def exportCamera(self, viewId=0):
    
        lm = slicer.app.layoutManager()
        rw = lm.threeDWidget(viewId).threeDView().renderWindow()
        camera = rw.GetRenderers().GetFirstRenderer().GetActiveCamera()
        
        data = {}
        data['focal_point'] = list(camera.GetFocalPoint())
        data['position'] = list(camera.GetPosition())
        data['view_up'] = list(camera.GetViewUp())
        data['view_angle'] = camera.GetViewAngle()
        if camera.GetParallelProjection():
            data['parallel_scale'] = camera.GetParallelScale()
        return data

    def exportModelsToDirectory(self, baseDir):
        
        dataDir = os.path.join(baseDir, 'data')
        if not os.path.isdir(dataDir):
            os.makedirs(dataDir)
        
        scene = {}
        
        scene['background_color'] = [0.7568627450980392, 0.7647058823529412, 0.9098039215686275]
        scene['background_color2'] = [0.4549019607843137, 0.4705882352941176, 0.7450980392156863]
        scene['camera'] = self.exportCamera()
        
        objects = []
        scene['objects'] = objects
    
        numModels = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLModelNode')
        for modelIndex in range(numModels):
            model = slicer.mrmlScene.GetNthNodeByClass(modelIndex, 'vtkMRMLModelNode')
            modelData = self.exportModel(model, dataDir)
            if modelData:
                objects.append(modelData)
        
        jsonStr = json.dumps(scene, indent=2)
        jsonStr = jsonStr.replace(baseDir + os.sep, '')
        sceneFile = os.path.join(baseDir, 'scene.kiwi')
        open(sceneFile, 'w').write(jsonStr)
      
    def zipDir(self, inputDirectory, zipPath):

        assert os.path.isdir(inputDirectory)

        inputDirectory = os.path.abspath(inputDirectory)
        parentDirectory = os.path.dirname(inputDirectory) + os.sep

        with contextlib.closing(zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)) as archive:
            for root, dirs, files in os.walk(inputDirectory):
                for filename in files:
                    absoluteFilename = os.path.join(root, filename)
                    relativeFilename = absoluteFilename[len(parentDirectory):]
                    print('  adding %s' % relativeFilename)
                    archive.write(absoluteFilename, relativeFilename)
    
    def getExportFolderName(self):
        timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
        return 'SlicerToKiwiExport-' + timestamp
    
    def exportModels(self, outFile=None):
        """
        Export visible models to a zip archive bundling KiwiViewer
        scene file and associated data.
        """
        
        if not outFile:
          outFile = os.path.join(slicer.app.temporaryPath, self.getExportFolderName() + '.kiwi.zip')
        
        folderName = os.path.splitext(os.path.basename(outFile))[0]
        outDir = os.path.join(os.path.dirname(outFile), folderName)

        print 'exporting to %s' % outDir
        self.exportModelsToDirectory(outDir)
        print 'exporting to %s - DONE' % outDir
        
        print 'zipping to %s' % outFile
        self.zipDir(outDir, outFile)
        print 'zipping to %s - DONE' % outFile

