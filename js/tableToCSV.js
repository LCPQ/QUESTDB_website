function tableToCSV(table) {
  var csv = [];
  var caption = $(table).find('caption').text()
  if (caption) {
    csv.push([`# ${caption}`])
  }
  const csvtextKey="csvtext"
  for (const row of Array.from(table[0].rows)) {
    const rowArray=[]
    for (const cell of Array.from(row.cells)) {
      var copycell=$(cell).clone()
      if (MathJax) {
        for (const jax of MathJax.Hub.getAllJax(cell)) {
          const sourceId = jax.SourceElement().id
          const txt = jax.originalText
          const frame = $(copycell).find(`#${sourceId}-Frame`)
          $(frame).remove()
          const script = $(copycell).find(`#${sourceId}`)
          $(script).replaceWith($("<span/>").text(`$${txt}$`))
        }
      }
      for (const replace of Array.from(copycell.find(`[data-${csvtextKey}]`))) {
        $(replace).replaceWith($("<span/>").text($(replace).data(csvtextKey))) 
      }
      var text = copycell.text()
      var text = copycell.text()
      if (text !== "" && !checkNumber(text)) {
        text = text.split('\u2011').join('-')
        text = `"${text}"`
      }
      rowArray.push(text)
    }
    csv.push(rowArray)
  }
  for (const row of Array.from(table[0].rows)) {
    for (const cell of Array.from(row.cells)) {
      const rowspan = cell.rowSpan
      const columnspan = cell.colSpan
      const colindex = cell.cellIndex
      const rowIndex = cell.parentNode.rowIndex
      if (columnspan>1) {
        for (let i = 1; i < rowspan; i++) {
          csv[rowIndex].splice(colindex,0,csv[rowIndex][colindex])
        }        
      }
      if (rowspan>1) {
        for (let i = 0; i < columnspan; i++) {
          for (let j = 1; j < rowspan; j++) {
            csv[rowIndex+j].splice(colindex,0,csv[rowIndex][colindex])
          }
        }
      }
    }
  }
  return csv.map(row=>row.join(",")).join("\n")
}