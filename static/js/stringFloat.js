class stringFloat{
  constructor(value) {
    this.string=value
  }
  get Value(){
    return parseFloat(this.string)
  }
  valueOf() {
    return this.Value;
  }
  toString(){
    if (isNaN(checkFloat(this.Value))) {
      return this.Value
    } else {
      return this.string
    }
  }
}