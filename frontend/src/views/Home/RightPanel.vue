<template>
  <div class="table-right-panel">
    <header>
      <el-button
        class="save-btn"
        type="info"
        round
        :disabled="!selectTable || !selectTable.tableInfo"
        @click="confirmIndentify"
      >Save the table position and start table structure recognition</el-button>
    </header>
    <InnerLine ref="innerLine" v-loading="innerLineLoading" :cells="cellData" :rows="rowList" :cols="colList" :url="imgUrl" @updateConfirmed="updateInnerConfirmed" />
    <header v-if="cellData.length">
      <el-button
        class="save-btn"
        type="info"
        round
        :disabled="!cellData.length"
        style="margin-top: 32px;"
        @click="confirmInnerLine"
      >Save the table structure and start content recognition</el-button>
    </header>
    <div v-if="newTableData.length" id="cellInfo" @afterMergeCells="showMerge" />
    <div v-if="newTableData.length" style="text-align: center;margin-top:16px;">
      <el-checkbox v-model="interchange"> Row to Column Interchange</el-checkbox>
    </div>
    <div v-if="newTableData.length" style="text-align: center;margin-top:16px;">
      <!-- <el-button class="save-btn" type="info" :disabled="!tableData.length" @click="saveTableContent">Save</el-button> -->
      <el-button class="save-btn" type="info" :disabled="!tableData.length" @click="downloadTable">Download</el-button>
    </div>
    <a v-show="false" ref="download" href="javascript:void(0)" @click="downloadExcel" />
  </div>
</template>
<script>
import Handsontable from 'handsontable'
import 'handsontable/dist/handsontable.full.css'
import { getTableInnerLine, getTableImage, getTableContent, updateTableContent, downloadTable } from '@/api/file'
import InnerLine from '@/components/InnerLine'
export default {
  components: { InnerLine },
  props: {
    selectTable: {
      type: Object,
      default: () => {}
    },
    fileId: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      imgList: [],
      tableZip: '',
      pageWithTable: [],
      currentIndex: 0,
      projectId: 0,
      tableId: 0,
      HandsonObj: null,
      tableData: [['', 'Tesla', 'Volvo', 'Toyota', 'Ford'],
        ['2019', 10, 11, 12, 13],
        ['2020', 20, 11, 14, 13],
        ['2021', 30, 15, 12, 13]],
      newTableData: [],
      tableOptions: {
        data: this.tableData,
        rowHeaders: false,
        colHeaders: false,
        // contextMenu: ['mergeCells', 'remove_row', 'remove_col', 'copy', 'cut', 'undo', 'redo'],
        contextMenu: true,
        mergeCells: [],
        afterMergeCells: this.handleMerge,
        afterUnmergeCells: this.handleUnMerge,
        afterChange: this.test
      },
      mergeCells: [],
      cellData: [],
      colList: [],
      rowList: [],
      imgUrl: '',
      innerLineLoading: false,
      innerTableConfirmed: false,
      innerContentConfirmed: false,
      downloadUrl: '',
      interchange: false,
      ocrInfo: {},
      currentPage: -1,
      apiInnerResult: {},
      apiInnerFiObj: {},
      apiInnerContent: {}
    }
  },
  watch: {
    tableInfo() {
      // 获取识别表格
      // this.getTableResult()
    },
    selectTable() {
      this.newTableData = []
      // this.cellData = []
      // this.imgUrl = ''
    }
  },
  mounted() {
    this.projectId = this.$route.params.projectId
    // this.initTableCell()
  },
  methods: {
    // 获取识别表格结果
    getTableResult() {

    },
    // 开始识别
    confirmIndentify() {
      // 调用后端接口
      const { elementWidth, elementHeight } = this.selectTable.pageInfo
      const { table_id, page, x1, y1, x2, y2, confirmed, direction } = this.selectTable.tableInfo
      const realX1 = x1 / elementWidth
      const realX2 = x2 / elementWidth
      const realY1 = y1 / elementHeight
      const realY2 = y2 / elementHeight
      const params = {
        table_id,
        page: page,
        x1: realX1,
        x2: realX2,
        y1: realY1,
        y2: realY2,
        confirmed,
        direction
      }
      this.currentPage = page
      this.tableId = table_id
      this.$emit('saveSuccess', this.tableId)
      this.fetchInnerImage(params)

      // if (!confirmed) {
      //   updateTableOutLine(params).then(res => {
      //     this.$emit('saveSuccess', res)
      //     this.tableId = res
      //     this.fetchInnerImage(this.fileId, params)
      //   })
      // } else {
      //   this.fetchInnerImage(this.fileId, params)
      // }
    },
    fetchInnerImage(params) {
      this.innerLineLoading = true
      getTableImage(this.fileId, JSON.stringify(params)).then(res => {
        this.imgUrl = `data:image/jpg;base64,${res.img}`
        this.fetchInnerLine(params)
      }).catch(() => {
        this.innerLineLoading = false
      })
    },
    fetchInnerLine(params) {
      this.colList = []
      this.rowList = []
      this.cellData = []
      getTableInnerLine(this.fileId, JSON.stringify(params)).then(res => {
        this.apiInnerResult = res
        const data = JSON.parse(res.fi)
        this.apiInnerFiObj = data
        this.innerLineLoading = false
        const { columns, rows, cells, confirmed } = data
        // this.ocrInfo = res[1]
        this.colList = columns || []
        this.rowList = rows || []
        this.innerTableConfirmed = confirmed
        cells.forEach(item => {
          item.forEach(i => {
            this.cellData = this.cellData.concat(i)
          })
        })
      }).catch(() => {
        this.innerLineLoading = false
      })
    },
    updateInnerConfirmed() {
      this.innerTableConfirmed = false
    },
    handleCellsStructure(cells, maxLength) {
      const length = maxLength <= 0 ? 0 : maxLength
      const cellList = []
      for (let i = 0; i < length; i++) {
        const cellItemList = []
        cells.forEach(item => {
          if (item.row_begin === i) {
            cellItemList.push(item)
          }
        })
        cellList.push(cellItemList)
      }
      return cellList
    },
    confirmInnerLine() {
      const lineCmpt = this.$refs.innerLine
      const { absoluteCols, absoluteRows, cellInfoList } = lineCmpt
      const cells = cellInfoList.map(item => item.cell)
      const data = {
        columns: absoluteCols,
        rows: absoluteRows,
        cells: this.handleCellsStructure(cells, absoluteRows.length - 1),
        confirmed: true
      }
      // handle cells 
      const newFiObj = Object.assign(this.apiInnerFiObj, data)
      const params = Object.assign(this.apiInnerResult, { fi: JSON.stringify(newFiObj)})
      this.getTableContentInfo(params)
      // if (!this.innerTableConfirmed) {
      //   // 若有改动，则调用api，保存内框线
      //   updateInnerLine(this.projectId, this.fileId, this.tableId, params).then(() => {
      //     this.innerTableConfirmed = true
      //     this.getTableContentInfo(params)
      //   })
      // } else {
      //   this.getTableContentInfo(params)
      // }
    },
    getTableContentInfo(params) {
      getTableContent(this.fileId, JSON.stringify(params)).then(res => {
        const { tableData, mergeCells } = res
        this.apiInnerContent = res
        this.tableData = tableData || [[]]
        this.newTableData = tableData
        this.tableOptions.mergeCells = mergeCells
        this.mergeCells = []
        this.$nextTick(() => {
          this.initTableCell()
        })
      })
    },
    // 初始化内框线表格
    initTableCell() {
      if (this.HandsonObj) this.HandsonObj.destroy()
      const container = document.getElementById('cellInfo')
      this.$set(this.tableOptions, 'data', this.tableData)
      // this.tableOptions.data = this.tableData
      this.HandsonObj = new Handsontable(
        container,
        this.tableOptions
      )
      // this.HandsonObj.getSettings()
    },
    saveTableContent() {
      const tableMeta = this.HandsonObj.getSettings()
      const data = tableMeta.data
      const params = {
        mergeCells: this.mergeCells,
        tableData: data
      }
      updateTableContent(this.projectId, this.fileId, this.tableId, { content: JSON.stringify(params) }).then(() => {
        this.$message({
          type: 'success',
          message: 'Save successfully!'
        })
      })
    },
    downloadTable() {
      let fd = new FormData();
      fd.append("content", JSON.stringify(this.apiInnerContent));
      downloadTable(this.fileId, this.interchange, fd).then(res => {
        this.arrayBufferToBase64(res)
      })
      // const tableMeta = this.HandsonObj.getSettings()
      // const data = tableMeta.data
      // const params = {
      //   mergeCells: this.mergeCells,
      //   tableData: data
      // }
      // downloadTable(this.fileId, this.tableId, this.currentPage).then(res => {
      //   this.arrayBufferToBase64(res)
      // })
      // 先保存，后下载
      // updateTableContent(this.projectId, this.fileId, this.tableId, { content: JSON.stringify(params) }).then(() => {
      //   // 勾选是否行列互换
      //   const intercharge = { trans_flag: this.interchange ? 'trans' : 'normal' }
      //   tableRowToCol(this.projectId, this.fileId, this.tableId, { info: JSON.stringify(intercharge) }).then(() => {
      //     downloadTable(this.projectId, this.fileId, this.tableId).then(res => {
      //       this.arrayBufferToBase64(res)
      //     })
      //   })
      // }).catch(() => {
      //   this.$notify.error({
      //     title: 'Error',
      //     message: 'Error, Please try again!'
      //   })
      // })
    },
    arrayBufferToBase64(data) {
      const blob = new Blob([data], {
        type: 'application/vnd.ms-excel;charset=utf-8'
      })
      this.downloadUrl = window.URL.createObjectURL(blob)
      this.$refs.download.click()
    },
    downloadExcel() {
      window.open(this.downloadUrl)
    },
    showMerge(data) {
      console.log('data sort ', data)
    },
    handleMerge(changes) {
      const to = changes.to
      const from = changes.from
      const mergeCellItem = {
        row: from.row,
        rowspan: to.row - from.row + 1,
        col: from.col,
        colspan: to.col - from.col + 1
      }
      const index = this.getMergeListIndex(mergeCellItem, this.mergeCells)
      if (index === -1) {
        this.mergeCells.push(mergeCellItem)
        this.innerContentConfirmed = true
      }
    },
    handleUnMerge(changes) {
      const to = changes.to
      const from = changes.from
      const mergeCellItem = {
        row: from.row,
        rowspan: to.row - from.row + 1,
        col: from.col,
        colspan: to.col - from.col + 1
      }
      const index = this.getMergeListIndex(mergeCellItem, this.mergeCells)
      if (index !== -1) {
        this.mergeCells.splice(index, 1)
        this.innerContentConfirmed = true
      }
    },
    getMergeListIndex(item, list) {
      const index = list.findIndex(listItem => {
        return (item.row === listItem.row) && (item.rowspan === listItem.rowspan) && (item.col === listItem.col) && (item.colspan === listItem.colspan)
      })
      return index
    }
  }
}
</script>
<style lang="less">
#hot-display-license-info {
  display: none;
}
.handsontable {
  .wtHolder {
    width: 100% !important;
    height: fit-content !important;
  }
}
</style>
<style lang="less" scoped>
.result-content {
  margin-top: 24px;
  .result-img {
    position: relative;
    width: 50%;
    min-width: 500px;
    margin: auto;
    // height: calc(100vh - 350px);
    // background: #f7f8fa;
  }
}
.save-btn {
  margin-bottom: 24px !important;
}
.el-pagination {
  display: inline-block;
  vertical-align: middle;
}
header {
  display: flex;
  align-items: center;
  justify-content: center;
}
.pagination {
  font-family: Source Han Sans SC;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  .pagination-item {
    margin: 0 8px;
    position: relative;
    .page-span {
      display: inline-block;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      border-radius: 50%;
      width: 20px;
      height: 20px;
      text-align: center;
      line-height: 20px;
      &.active {
        color: #83a7cf;
      }
    }
    .table-sign {
      position: absolute;
      top: -2px;
      left: calc(50% - 2px);
      display: inline-block;
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: #83a7cf;
    }
    .el-button {
      width: 32px;
      height: 32px;
      /* line-height: 30px; */
      text-align: center;
      padding: 0;
    }
  }
}

</style>
