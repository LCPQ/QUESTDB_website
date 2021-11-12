class GeometriesLoader{
  static async loadForAsync(array){
    var xyzs=[]
    for (const item of array) {
      const mymol=moleculeFormater.toFileName(item.molecule)
      const myset=item.set.replace('#','')
      try {
        const mol=await Geometry.loadXYZAsync(`/${myset}/${mymol}.xyz`)
        xyzs.push(mol)
      } catch (error) {
        console.error("Geometry not found",item,error)
      }
    }
    return xyzs.flat()
  }
}
