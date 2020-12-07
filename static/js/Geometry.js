class Geometry {
  constructor(molecule, comment) {
    this.molecule = molecule
    this.comment = comment
  }
  static async loadXYZAsync(file) {
    switch (trueTypeOf(file)) {
      case String.name:
        file = getFullDataPath("structures"+file)
        var str = getTextFromFileUrl(file)
        break;
      case File.name:
        var str = await getTextFromUploadedFileAsync(file)
        break
    }
    var xyz = this.loadXYZString(str);
    for (var geom of xyz){
      geom.sourceFile = new websiteFile(file)
    }
    return xyz
  }
  static loadXYZString(text) {
    var lines = text.split("\n")
    var indexes = lines.findAllIndexes((line) => {
      return line.match(/^\d+\s*$/)
    })
    indexes.push(lines.length)
    var geoms = []
    for (let i = 0; i < indexes.length - 1; i++) {
      const mollines = lines.slice(indexes[i], indexes[i + 1])
      const comment = mollines[1]
      const molecule = ChemDoodle.readXYZ(mollines.join("\n"))
      geoms.push(new Geometry(molecule, comment))
    }
    return geoms
  }
}
