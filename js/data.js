class excitationTypes {
  static get Valence() { return new excitationType(1, new description("Valence")) }
  static get Rydberg() { return new excitationType(1 << 1, new description("Rydberg")) }
  static get PiPis() { return new excitationType(1 << 2, new description(String.raw`\pi \rightarrow \pi^\star`, true)) }
  static get nPis() { return new excitationType(1 << 3, new description(String.raw`n \rightarrow \pi^\star`, true)) }
  static get Single() { return new excitationType(1 << 4, new description("Single")) }
  static get Double() { return new excitationType(1 << 5, new description("Double")) }
  static get SingletSinglet() { return new excitationType(1 << 6, new description(String.raw`\mathrm{Singlet} \rightarrow \mathrm{Singlet}`, true)) }
  static get SingletTriplet() { return new excitationType(1 << 7, new description(String.raw`\mathrm{Singlet} \rightarrow \mathrm{Triplet}`, true)) }
  static get DoubletDoublet() { return new excitationType(1 << 8, new description(String.raw`\mathrm{Doublet} \rightarrow \mathrm{Doublet}`, true)) }
  // Max bit shifts is 31 because int are int32 So 1 << 31 are -2147483648
  static get Others() { return new excitationType(1 << 31, new description("Others")) }
  static get All() { return EnumUltils.getAll(this, excitationType) }
  static GetFlags(value) { return EnumUltils.GetFlags(value, this, excitationType) }
}

class EnumUltils {
  static getAll(enumClass, valueType) {
    var lst = []
    for (const prop of Object.getOwnPropertyNames(enumClass)) {
      if (prop != "All") {
        const value = enumClass[prop]
        if (trueTypeOf(value) == valueType.name) {
          lst.push([prop, value])
        }
      }
    }
    return lst
  }
  static GetFlags(value, enumClass, valueType) {
    return this.getAll(enumClass, valueType).filter(x => value & x[1])
  }
}

class description {
  constructor(string, isLaTeX = false) {
    this.string = string
    this.isLaTeX = isLaTeX
  }
}
class DescribedValueBase {
  constructor(value, description) {
    this.Value = value;
    this.description = description
  }
  valueOf() {
    return this.Value;
  }
}

class excitationType extends DescribedValueBase {
}
class VertExcitationKind extends DescribedValueBase {

}
class code {
  constructor(name, version) {
    this.name = name;
    this.version = version;
  };
  toString() {
    var str = this.name;
    if (this.version) {
      str = str + ' (' + this.version + ')';
    }
    return str;
  }
  static fromString(str) {
    var vals = str.split(",")
    if (vals.length >= 2) {
      return new code(vals[0], vals[1]);
    } else {
      return new code(vals[0], null);
    }
  }
}
class method {
  constructor(name, basis = null) {
    this.name = name;
    this.basis = basis;
  }
  static fromString(str) {
    var vals = str.split(",")
    if (vals.length == 2) {
      return new method(vals[0], vals[1]);
    }
    else {
      return new method(vals[0], null)
    }
  }
  toString(separator = "/") {
    var str = this.name;
    if (this.basis) {
      str = str + separator + this.basis;
    }
    return str;
  }
  get isTBE() {
    return /^TBE/.test(this.name)
  }
}

class state {
  constructor(number, multiplicity, symmetry) {
    this.number = number;
    this.multiplicity = multiplicity;
    this.symmetry = symmetry;
  };
  toString() {
    var str = this.number + ' ^' + this.multiplicity + this.symmetry;
    return str;
  };
  toLaTeX() {
    var tex = String.raw`${this.number}\:^{${this.multiplicity}}\mathrm{${this.symmetry}}`;
    return tex;
  };
}
class exSet{
  constructor(name,index)
  {
    this.name = name
    this.index = index
  }

  static fromString(str) {
    var vals = str.split(",")
    var myset
    if (vals.length >= 2) {
      return new exSet(vals[0], parseInt(vals[1],10));
    } else {
      return new exSet(vals[0], 0);
    }
  }
  async getDOIAsync()
  {
    let db = await indexDB.loadAsync()
    if (db.sets.has(this.name)) {
      return db.sets.get(this.name)[this.index]
    }
  }
  toString()
  {
    return `${this.name},${this.index}`
  }
  isSameSet(set)
  {
    return this.name == set.name
  }
  async isSameArticleAsync(set)
  {
    if (this.name===set.name && this.index===set.index) {
      return true
    }
    else
    {
      return await this.getDOIAsync() === await set.getDOIAsync()
    }
  }
}
class excitationBase {
  constructor(initial, final, type = '', T1 = null) {
    this.initial = initial;
    this.final = final
    this.type = new excitationType(0, new description(type, true))
    if (type) {
      const tys = type.split(";")
      const arrow = String.raw`\rightarrow`
      for (const ty of tys) {
        if (ty.includes(arrow)) {
          const [initialt, finalt] = ty.split(arrow, 2)
          const initialts = initialt.split(",").map(x => x.trim())
          const finalts = finalt.split(",").map(x => x.trim())
          if (initialts.length == 2 && finalts.length == 2) {
            this.type.Value = this.type | excitationTypes.Double
          }
          else if (initialts.length == 1 && finalts.length == 1) {
            this.type.Value = this.type | excitationTypes.Single
          }
          if (initialts.includes("n") && finalts.includes(String.raw`\pi^\star`)) {
            this.type.Value = this.type | excitationTypes.nPis
          } else if (initialts.includes(String.raw`\pi`) && finalts.includes(String.raw`\pi^\star`)) {
            this.type.Value = this.type | excitationTypes.PiPis
          }
        } else if (ty.includes(String.raw`\mathrm{R}`)) {
          this.type.Value = this.type | excitationTypes.Rydberg
        } else if (ty.includes(String.raw`\mathrm{V}`)) {
          this.type.Value = this.type | excitationTypes.Valence
        } else if (ty.toLowerCase()===excitationTypes.Double.description.string.toLowerCase()){
          this.type.Value = this.type | excitationTypes.Double
        }
      }
    }
    var m = new Map([
      [JSON.stringify([1, 1]), excitationTypes.SingletSinglet],
      [JSON.stringify([2, 2]), excitationTypes.DoubletDoublet],
      [JSON.stringify([1, 3]), excitationTypes.SingletTriplet],
    ])
    const marray = JSON.stringify([initial.multiplicity, final.multiplicity])
    if (m.has(marray)) {
      this.type.Value = this.type.Value | m.get(marray)
    }
    if (this.type.Value == 0) {
      this.type.Value = excitationTypes.Others.Value;
    }
    else if (!(this.type & (excitationTypes.Single.Value | excitationTypes.Double.Value))){
      this.type.Value += excitationTypes.Single.Value
    }
    this.T1 = T1
  }
}
class excitationValue extends excitationBase {
  constructor(initial, final, type, value, oscilatorForces = null, T1 = null, isUnsafe = false) {
    super(initial, final, type, T1)
    this.value = value
    this.oscilatorForces = oscilatorForces
    this.isUnsafe = isUnsafe
  }
}

class dataFileBase {
  constructor() {
    this.molecule = ''
    this.comment = ""
    this.code = null
    this.method = null
    this.excitations = []
    this.set = null
    this.sourceFile = null
  }
  static _GetMetaRexEx() {
    //metadata RegExp (start with #; maybe somme spaces; : ; maybe somme space; datas)
    return /^#\s*([A-Za-z_]+)\s*:\s*(.*)$/;
  }
  async getGeometryAsync(state = null) {
    var site_url = "/"+window.location.pathname.split('/')[1];
    // var text = await getTextFromFileUrlAsync(`/data/structures/${this.set.name.replace("#", "")}/${this.molecule.toLowerCase()}.xyz`)
    var text = getTextFromFileUrl(site_url+`/data/structures/${this.set.name.replace("#", "")}/${this.molecule.toLowerCase()}.xyz`)
    var lines = text.split("\n")
    var indexes = lines.findAllIndexes((line) => {
      return line.match(/^\d+$/)
    })
    indexes.push(lines.length)
    var molsstr = []
    for (let i = 0; i < indexes.length - 1; i++) {
      molsstr.push(lines.slice(indexes[i], indexes[i + 1]).join('\n'))
    }
    molsstr.filter((molstr) => {
      var params = molstr.split("\n")[1].split(",")
      return (state === null || params[0] === `^${state.multiplicity}${state.symmetry}`) && params[1] == `${this.method.name},${this.method.basis}`
    })
    return molsstr.map((molstr) => {
      var params = molstr.split("\n")[1].split(",")
      var regex=/^\^(\d+)(.+)$/
      var m=params[1].match(regex)
      return {
        name: this.molecule,
        multiplicity:m[1],
        symmetry:m[2],
        method:this.geometry,
        geometry:ChemDoodle.readXYZ(molstr)
      }
    })
  }
  CopyExcitationsTypeFrom(data) {
    var exc_strings = data.excitations.map( e => [e, JSON.stringify(e.initial), JSON.stringify(e.final) ] )
    for (const ex of this.excitations) {
      const exi = JSON.stringify(ex.initial)
      const exf = JSON.stringify(ex.final)
      const ex2 = exc_strings.find((e) => {
        return (e[1]=== exi) && (e[2]=== exf)
      })
      if (ex2 !== undefined) {
        if (DebugMode.Enabled) {
          const restflag=ex.type.Value & ex2[0].type.Value
          const result=restflag==ex.type.Value
          console.assert(result, "Excitation type error", data.molecule, ex, ex2[0], this.sourceFile)
        }
        ex.type = ex2[0].type
      }
    }
  }
  static async loadAsync(file, kind = undefined) {
    switch (trueTypeOf(file)) {
      case String.name:
        file = getFullDataPath(file)
        // const maxAge= (DebugMode.Enabled,0,600)
        // var str = await getTextFromFileUrlAsync(file,{"Cache-Control":`max-age=${maxAge}`})
        var str = getTextFromFileUrl(file)
        break;
      case File.name:
        var str = await getTextFromUploadedFileAsync(file)
        break
    }
    var dat = this.loadString(str, kind);
    dat.sourceFile = new websiteFile(file)
    return dat
  }
  static load(file, kind = undefined) {
    switch (trueTypeOf(file)) {
      case String.name:
        file = getFullDataPath(file)
        var str = getTextFromFileUrl(file)
        break;
      case File.name:
        var str = (async () => await getTextFromUploadedFileAsync(file))().then(x=>x)
        break
    }
    var dat = this.loadString(str, kind);
    dat.sourceFile = new websiteFile(file)
    return dat
  }
  _OnReadMetaPair(key, value) {
    switch (key) {
      case "molecule":
        this.molecule = value
        break;
      case "comment":
        this.comment = value
        break;
      case "code":
        this.code = code.fromString(value)
        break;
      case "method":
        this.method = method.fromString(value)
        break;
      case "set":
        this.set = exSet.fromString(value)
        break;
    }
  }
  _OnReadRow(line) {
    var vals = line.match(/\([^\)]+\)|\S+/g)
    var start = new state(parseInt(vals[0], 10), parseInt(vals[1], 10), vals[2]);
    var end = new state(parseInt(vals[3], 10), parseInt(vals[4], 10), vals[5]);
    var type = ((vals.length >= 7) ? vals[6] : null)
    if (type === "_") {
      type = null
    }
    if (type) {
      const m = type.match(/^\(([^\)]*)\)$/)
      if (m) {
        type = m[1]
      }
    }
    var val = ((vals.length >= 8) ? new stringNumber(vals[7]) : NaN)
    var T1 = ((vals.length >= 9) ? new stringNumber(vals[8]) : NaN)
    var oscilatorForces = ((vals.length >= 10) ? new stringNumber(vals[9]) : NaN)
    var isUnsafe = ((vals.length >= 11) ? vals[10] === true.toString() : false)
    var ex = new excitationValue(start, end, type, val, oscilatorForces, T1, isUnsafe);
    if (this.VertExcitationKind) {
      ex.VertExcitationKind = this.VertExcitationKind
    }
    return ex;
  };
  _OnReadMeta(line) {
    // get key value
    var match = line.match(dataFileBase._GetMetaRexEx())
    // normalize key to lower
    var key = match[1].toLowerCase()
    //if data has value
    if (match.length == 3 && match[2]) {
      var val = match[2]
      this._OnReadMetaPair(key, val)
    }
  }
  static loadString(text, kind = null) {
    // for each line with metadata
    var ismetaArea = true;
    var dat = new VertDataFile()
    for (var line of text.split("\n")) {
      //if it's not empty line
      line = line.trim();
      if (line) {
        //if # may be metadata or comment
        if (line.charAt(0) == "#") {
          //if it's metadata
          if (ismetaArea && dataFileBase._GetMetaRexEx().test(line)) {
            dat._OnReadMeta(line);
          }
        } else { //else its row
          ismetaArea = false;
          dat.excitations.push(dat._OnReadRow(line, kind));
        }
      }
    }
    if (DebugMode.Enabled) {
      var stfy = dat.excitations.map(e => JSON.stringify([e.initial, e.final]))
      var double = []
      stfy.forEach(function (element, i) {
        // Find if there is a duplicate or not
        if (stfy.indexOf(element, i + 1) >= 0) {
          // Find if the element is already in the result array or not
          if (double.indexOf(element) === -1) {
            double.push(dat.excitations[i])
          }
        }
      });
      console.assert(double.length === 0, "Double found", double, dat.molecule, dat.method.toString())
      if (dat.set!== null && dat.set !== "10.1021/acs.jctc.8b01205") {
        for (const ex of dat.excitations) {
          console.assert(Number.isNaN(ex.T1.valueOf()) | ex.T1 > 50 | ex.isUnsafe == true, "should be unsafe", dat, ex)
        }
        for (const ex of dat.excitations) {
          console.assert(JSON.stringify(ex.initial)!==JSON.stringify(ex.final),"Final must be different to initial", dat, ex)
        }
      }
    }
    return dat
  }
}
class VertExcitationKinds {
  static get Absorbtion() { return new VertExcitationKind(1, new description("Absorption")) }
  static get Fluorescence() { return new VertExcitationKind(1 << 1, new description("Fluorescence")) }
  static get All() { return EnumUltils.getAll(this, VertExcitationKind) }
  static GetFlags(value) { return EnumUltils.GetFlags(value, this, VertExcitationKind) }
}
class VertDataFile extends dataFileBase {
  constructor(VertExcitationKind) {
    super()
    this.VertExcitationKind = VertExcitationKind
    this.geometry = null
  }
  _OnReadMetaPair(key, value) {
    if (key == "geom") {
      this.geometry = method.fromString(value)
    }
    else {
      super._OnReadMetaPair(key, value)
    }
  }
  _OnReadRow(line, kind) {
    var ex = super._OnReadRow(line)
    ex.VertExcitationKind = kind
    return ex
  }
}
