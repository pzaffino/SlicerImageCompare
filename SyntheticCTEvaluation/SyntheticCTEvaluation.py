import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

from slicer.util import setSliceViewerLayers
import numpy as np
import SimpleITK as sitk
import sitkUtils

#
# SyntheticCTEvaluation
#

class SyntheticCTEvaluation(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Synthetic CT evaluation" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Quantification"]
    self.parent.dependencies = []
    self.parent.contributors = ["Paolo Zaffino (Magna Graecia University of Catanzaro, Italy)", "Maria Francesca Spadea (Magna Graecia University of Catanzaro, Italy)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = '''
This module quatifies conversion accuracy of a synthetic CT algorithm.
The full validation workflow is described in Spadea, Maria Francesca, et al. "Deep Convolution Neural Network (DCNN) Multiplane Approach to Synthetic CT Generation From MR images—Application in Brain Proton Therapy." International Journal of Radiation Oncology* Biology* Physics 105.3 (2019): 495-503.
'''
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """ """ # replace with organization, grant and thanks.

#
# SyntheticCTEvaluationWidget
#

class SyntheticCTEvaluationWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """


  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # GT CT volume selector
    #
    self.gtCTSelector = slicer.qMRMLNodeComboBox()
    self.gtCTSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.gtCTSelector.selectNodeUponCreation = True
    self.gtCTSelector.addEnabled = False
    self.gtCTSelector.removeEnabled = False
    self.gtCTSelector.noneEnabled = False
    self.gtCTSelector.showHidden = False
    self.gtCTSelector.showChildNodeTypes = False
    self.gtCTSelector.setMRMLScene( slicer.mrmlScene )
    self.gtCTSelector.setToolTip( "Select the ground truth CT" )
    parametersFormLayout.addRow("Ground truth CT volume: ", self.gtCTSelector)

    #
    # synthetic CT volume selector
    #
    self.sCTSelector = slicer.qMRMLNodeComboBox()
    self.sCTSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.sCTSelector.selectNodeUponCreation = True
    self.sCTSelector.addEnabled = False
    self.sCTSelector.removeEnabled = False
    self.sCTSelector.noneEnabled = False
    self.sCTSelector.showHidden = False
    self.sCTSelector.showChildNodeTypes = False
    self.sCTSelector.setMRMLScene( slicer.mrmlScene )
    self.sCTSelector.setToolTip( "Select the synthetic CT" )
    parametersFormLayout.addRow("Synthetic CT volume: ", self.sCTSelector)

    #
    # mask label selector
    #
    self.maskSelector = slicer.qMRMLNodeComboBox()
    self.maskSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    self.maskSelector.selectNodeUponCreation = True
    self.maskSelector.addEnabled = False
    self.maskSelector.removeEnabled = False
    self.maskSelector.noneEnabled = False
    self.maskSelector.showHidden = False
    self.maskSelector.showChildNodeTypes = False
    self.maskSelector.setMRMLScene( slicer.mrmlScene )
    self.maskSelector.setToolTip( "Select the labelmap within evaluation will be ran" )
    parametersFormLayout.addRow("Mask label: ", self.maskSelector)

    #
    # output volume selector
    #

    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Select or create a volume where the error map will be stored" )
    parametersFormLayout.addRow("Output error map volume: ", self.outputSelector)

    # MAE and ME QLabel
    self.QLabelMAE = qt.QLabel("")
    parametersFormLayout.addRow("Mean Absolute Error (MAE) [HU] = ", self.QLabelMAE)
    self.QLabelME = qt.QLabel("")
    parametersFormLayout.addRow("Mean Error (ME) [HU] = ", self.QLabelME)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.gtCTSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.sCTSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.maskSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

    # Create logic object
    self.logic = SyntheticCTEvaluationLogic()

  def cleanup(self):
    self.QLabelMAE.setText("")
    self.QLabelME.setText("")

  def onSelect(self):
    self.applyButton.enabled = self.gtCTSelector.currentNode() and self.sCTSelector.currentNode() and self.maskSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    mae, me = self.logic.run(self.gtCTSelector.currentNode().GetName(), self.sCTSelector.currentNode().GetName(), self.maskSelector.currentNode().GetName(), self.outputSelector.currentNode())
    self.QLabelMAE.setText("%.1f" % mae)
    self.QLabelME.setText("%.1f" % me)
#
# SyntheticCTEvaluationLogic
#

class SyntheticCTEvaluationLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):

    self.hasTable = False

  def binarizeNumpyMask(self, img_np):
   img_np = img_np.astype(np.float32)
   img_np -= img_np.min()
   img_np /= img_np.max()
   img_np[img_np>0.5]=1
   img_np[img_np<=0.5]=0
   return img_np.astype(np.uint8)

  def run(self, gtCTVolumeName, sCTVolumeName, maskVolumeName, outputVolume):
    """
    Run accuracy assessment.
    """

    # Get sitk/numpy images from Slicer
    gtCT_sitk = sitk.Cast(sitkUtils.PullVolumeFromSlicer(gtCTVolumeName), sitk.sitkFloat32)
    sCT_sitk = sitk.Cast(sitkUtils.PullVolumeFromSlicer(sCTVolumeName), sitk.sitkFloat32)
    mask_sitk = sitk.Cast(sitkUtils.PullVolumeFromSlicer(maskVolumeName), sitk.sitkLabelUInt8)
    mask_sitk = sitk.LabelMapToBinary(mask_sitk)
    #TODO: investigate better if mask is binary or not here

    gtCT = sitk.GetArrayFromImage(gtCT_sitk).astype(np.float32)
    sCT = sitk.GetArrayFromImage(sCT_sitk).astype(np.float32)
    mask = self.binarizeNumpyMask(sitk.GetArrayFromImage(mask_sitk))

    # Compute MAE and ME
    img_difference = gtCT - sCT

    img_difference[mask==0]=-1000
    img_difference_sitk = sitk.GetImageFromArray(img_difference)
    img_difference_sitk.CopyInformation(gtCT_sitk)

    img_difference[mask==0]=np.nan
    mae = np.nanmean(np.abs(img_difference).flatten())
    me = np.nanmean(img_difference.flatten())

    # If the table does not exist, create it
    if self.hasTable == False:

      self.hasTable = True

      # Create table
      self.tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode")
      self.table = self.tableNode.GetTable()
      arrX = vtk.vtkFloatArray()
      arrX.SetName("HU")
      self.table.AddColumn(arrX)

      arrY = vtk.vtkFloatArray()
      arrY.SetName("DSC")
      self.table.AddColumn(arrY)

      # Create plot node
      plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "Bone threshold segmentation")
      plotSeriesNode.SetAndObserveTableNodeID(self.tableNode.GetID())
      plotSeriesNode.SetXColumnName("HU")
      plotSeriesNode.SetYColumnName("DSC")
      plotSeriesNode.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
      plotSeriesNode.SetMarkerStyle(slicer.vtkMRMLPlotSeriesNode.MarkerStyleSquare)
      plotSeriesNode.SetUniqueColor()

      # Create plot chart node
      self.plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode")
      self.plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())
      self.plotChartNode.SetTitle('Bone threshold assessment')
      self.plotChartNode.SetXAxisTitle('[HU]')
      self.plotChartNode.SetYAxisTitle('DSC')
      self.plotChartNode.LegendVisibilityOff()

    # Fill table with DSC value for bone
    thrs = np.arange(100.0, 1100.0, 100.0)
    self.table.SetNumberOfRows(len(thrs))

    overlap_measures_filter = sitk.LabelOverlapMeasuresImageFilter()

    for i, thr in enumerate(thrs):
      gtCT_bin = sitk.BinaryThreshold(sitk.Mask(gtCT_sitk, mask_sitk, outsideValue=-1000), lowerThreshold=thr, upperThreshold=1500.0, insideValue=1, outsideValue=0)
      sCT_bin = sitk.BinaryThreshold(sitk.Mask(sCT_sitk, mask_sitk, outsideValue=-1000), lowerThreshold=thr, upperThreshold=1500.0, insideValue=1, outsideValue=0)

      overlap_measures_filter.Execute(gtCT_bin, sCT_bin)
      dsc = overlap_measures_filter.GetDiceCoefficient()

      # TODO: empty table before each run?
      self.table.SetValue(i, 0, thr)
      self.table.SetValue(i, 1, dsc)

    # Switch to a layout that contains a plot view to create a plot widget
    layoutManager = slicer.app.layoutManager()
    layoutWithPlot = slicer.modules.plots.logic().GetLayoutWithPlot(layoutManager.layout)
    layoutManager.setLayout(layoutWithPlot)

    # Select chart in plot view
    plotWidget = layoutManager.plotWidget(0)
    plotViewNode = plotWidget.mrmlPlotViewNode()
    plotViewNode.SetPlotChartNodeID(self.plotChartNode.GetID())

    # Show diff image
    outputVolume = sitkUtils.PushVolumeToSlicer(img_difference_sitk, outputVolume)
    setSliceViewerLayers(background=outputVolume)
    displayNode = outputVolume.GetDisplayNode()
    displayNode.SetAndObserveColorNodeID('vtkMRMLColorTableNodeRainbow')

    return mae, me

class SyntheticCTEvaluationTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_SyntheticCTEvaluation1()

  def test_SyntheticCTEvaluation1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767',
      checksums='SHA256:12d17fba4f2e1f1a843f0757366f28c3f3e1a8bb38836f0de2a32bb1cd476560')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = SyntheticCTEvaluationLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
