#!/usr/bin/env python
"""
Show the progress of Moving transformations associated to one or more datasets

Warning: Moving transformations are expected to follow the naming convention:
<Move>_<MCCampaign>_<datasetName>
Transformations not following this convention can be inspected directly using the Transformation Web Monitor or the transformation CLI

Usage:
   cta-prod-move-dataset-status <datasetName (may contain wild cards) or ascii file with a list of datasets> <MCCampaign> <target SE>

Example:
   cta-prod-move-dataset-status Paranal_gamma_North_20deg_HB9 PROD3 CC-IN2P3-Tape
"""

__RCSID__ = "$Id$"

import os

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient



def get_transformation_info(transID):

  transClient = TransformationClient()

  paramShowNames = [
      "TransformationID",
      "TransformationName",
      "Type",
      "Status",
      "Files_Total",
      "Files_PercentProcessed",
      "Files_Processed",
      "Files_Unused",
      "Jobs_TotalCreated",
      "Jobs_Waiting",
      "Jobs_Running",
      "Jobs_Done",
      "Jobs_Failed",
      "Jobs_Stalled",
  ]

  #trans_name = ("Move_%s_%s_%s" % (MCCampaign, targetSE, dataset_name))

  #res = transClient.getTransformationParameters(trans_name, 'TransformationID')
  #res = transClient.getTransformation(trans_name, 'TransformationID')

  #if not res['OK']:
    #gLogger.error("Warning: failed to get transformation %s" % (trans_name))
    #return "_"

  #transID = res['Value']
  res = transClient.getTransformationSummaryWeb({"TransformationID": transID}, [], 0, 1)

  if not res["OK"]:
      DIRAC.gLogger.error(res["Message"])
      DIRAC.exit(-1)

  if res["Value"]["TotalRecords"] > 0:
    paramNames = res["Value"]["ParameterNames"]
    for paramValues in res["Value"]["Records"]:
      paramShowValues = map(lambda pname: paramValues[paramNames.index(pname)], paramShowNames)
      showDict = dict(zip(paramShowNames, paramShowValues))
      files_PercentProcessed = showDict["Files_PercentProcessed"]
      transName = showDict["TransformationName"]

  return (transName, files_PercentProcessed)

#########################################################
@Script()
def main():

  Script.parseCommandLine()
  args = Script.getPositionalArgs()
  if (len(args) != 1):
    Script.showHelp()

  # get arguments
  transIDs = []
  for arg in args[0].split(','):
    if os.path.exists(arg):
      lines = open(arg, 'rt').readlines()
      for line in lines:
        for transID in line.split(','):
          transIDs += [int(transID.strip())]
    else:
      transIDs.append(int(arg))

    #tc = TransformationClient()
  values = []

  for transID in transIDs:
    #res = tc.deleteTransformation(transID)
    #get_transformation_info(transID)
    transName, files_PercentProcessed = get_transformation_info(transID)
    values.append((transName, files_PercentProcessed))


  # print table
  gLogger.notice('\n|_. Transformation Name |_. Files Processed (%)| ')
  for value in values:
    gLogger.notice("|%s|" % "|".join(map(str,value)))

  DIRAC.exit()

if __name__ == '__main__':
  main()
