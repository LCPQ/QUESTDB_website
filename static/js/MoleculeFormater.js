class moleculeFormater{
  static get __mathRegEx() {
    return /(?:(?<!\\)|(?<=\\{2}))\$(.*?)(?:(?<!\\)|(?<=\\{2}))\$/gi
  }
  static toWebLatex(string) {
    if(mhchemCE.test(string)) {
       return MathJaxUtils.getMathJaxString(string)
    }
    else {
      return string.replace(moleculeFormater.__mathRegEx,(v,p1)=>MathJaxUtils.getMathJaxString(p1))
    }
  }
  static toUnicode(string) {
    if (mhchemCE.test(string)) {
      return mhchemCE.extract(string)
    }
    else {
      return string.replace(moleculeFormater.__mathRegEx,(v,p1)=>{
        return texparser.parse_str(p1,0).text
      })
    }
  }
  static toFileName(string) {
    var molpart = string
    if (mhchemCE.test(molpart)) {
      molpart = mhchemCE.extract(molpart)
    }
    else {
      molpart = molpart.replace(moleculeFormater.__mathRegEx,(v,p1)=>{
        return p1.replace('\\','')
      })
    }
    return molpart.toLowerCase().replace(' ','_')
  }
}