import json
import os
import shutil

import requests as requests
from jsonschema import validate


def validateModJSON(mod):
    schema = json.loads(requests.get("https://withertech.com/SimpleModManagerMod.json").text)
    validate(mod, schema)


def getFiles(myFolder):
    for dirName, subdirList, fileList in os.walk(myFolder):
        for fname in fileList:
            yield os.path.relpath(os.path.join(dirName, fname), myFolder)


def clean(mod):
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build.zip"):
        os.remove("build.zip")
    if os.path.exists(mod["name"] + ".nxmod"):
        os.remove(mod["name"] + ".nxmod")


def copyFiles(mod):
    os.mkdir("build")
    shutil.copy("mod.json", "build")
    shutil.copy(mod["icon"], "build")
    shutil.copytree("data", "build/data")


def createManifest():
    oldPath = os.getcwd()
    os.chdir("build")
    manifest = open("MANIFEST", "w")

    for file in getFiles("data"):
        manifest.write(file + "\n")
    os.chdir(oldPath)


def pack(mod):
    os.mkdir("dist")
    shutil.make_archive("build", "zip", "build")
    os.rename("build.zip", os.path.join("dist", mod["name"] + ".nxmod"))


def run(args):
    os.chdir(args.path)
    mod = json.load(open("mod.json"))
    validateModJSON(mod)
    clean(mod)
    copyFiles(mod)
    createManifest()
    pack(mod)
