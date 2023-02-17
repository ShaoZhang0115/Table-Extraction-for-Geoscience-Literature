<template>
  <div>
    <!-- <div v-if="false" class="demo-list" :style="{'grid-template-columns': cols.map(i => `${i * 100}%`).join(' '), 'grid-template-rows': rows.map(i => `${i * 100}%`).join(' ') }">
      <VueResizable
        v-for="(item,index) in cells"
        :key="index"
        :active="resizeActive"
        class="table-cell"
        :style="{'grid-column-start': item[0], 'grid-column-end': item[1], 'grid-row-start': item[2], 'grid-row-end': item[3] }"
        @resize:move="resizeMove($event, item)"
        @resize:start="resizeStart($event, item)"
      >
        <div>
          {{ index + 1 }}
        </div>
      </VueResizable>
    </div> -->
    <div v-show="url" class="position-container">
      <img ref="innerImg" :src="url" alt="" srcset="" width="100%" height="100%">
      <VueResizable
        v-for="(item,index) in cellInfoList"
        :key="index"
        :active="resizeActive"
        :width="(item.colEnd - item.colStart) * imgWidth"
        :height="(item.rowEnd - item.rowStart) * imgHeight"
        :left="item.colStart * imgWidth"
        :top="item.rowStart * imgHeight"
        :style="{'background-color': findCellIndex(item.cell, selectedCell) === -1 ? 'transparent' : 'rgba(0,0,0,0.1)'}"
        :min-width="1"
        :min-height="1"
        :max-height="calcMaxHeight(item)"
        :max-width="calcMaxWidth(item)"
        @resize:move="resizeMove($event, item)"
        @resize:start="resizeStart($event, item)"
        @contextmenu.prevent.native="showContextMenu($event, item)"
        @mousedown.prevent.native="handleMouseDown($event, item)"
        @mouseup.prevent.native="handleMouseUp(item)"
        @mouseenter.prevent.native="handleMouseMove(item)"
      >
        <!-- :style="{'top': `${item.rowStart * 500}px`, 'left': `${item.colStart * 500}px`, 'width': `${(item.colEnd - item.colStart) * 500}px`, 'height': `${(item.rowEnd - item.rowStart) * 500}px`}" -->
        <!-- {{ index }} -->
      </VueResizable>
    </div>
    <ul v-if="isShowContextMenu" :style="{'left': menuX + 'px', 'top': menuY + 'px' }" class="context-menu">
      <li v-for="item in contextList" :key="item.value" class="menu-item" @click="handleMenuClick(item)">{{ item.label }}</li>
    </ul>
  </div>
</template>
<script>
import VueResizable from 'vue-resizable'
const _ = require('lodash')
export default {
  components: { VueResizable },
  props: {
    // 从0开始
    cells: {
      type: Array,
      default: () => []
    },
    cols: {
      type: Array,
      default: () => []
    },
    rows: {
      type: Array,
      default: () => []
    },
    url: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      resizeActive: ['r', 'b', 'l', 't'],
      // cols: [0.2, 0.3, 0.5],
      // rows: [0.3, 0.3, 0.4],
      // 从1开始 [grid-column-start, grid-column-end, grid-row-start, grid-row-end]
      // cells: [
      //   [1, 2, 1, 2],
      //   [2, 3, 1, 2],
      //   [3, 4, 1, 2],
      //   [1, 3, 2, 4],
      //   [3, 4, 2, 3],
      //   [3, 4, 3, 4]
      // ],
      // absoluteCols: [0.1, 0.2, 0.5, 0.8],
      // absoluteRows: [0, 0.3, 0.4, 0.9],
      absoluteCols: [],
      absoluteRows: [],
      cellInfoList: [],
      offsetTop: 0,
      offsetLeft: 0,
      currentTop: 0,
      currentLeft: 0,
      currentHeight: 0,
      currentWidth: 0,
      currentItem: null,
      isShowContextMenu: false,
      menuX: 0,
      menuY: 0,
      contextList: [],
      classNameMap: {
        'resizable-component': 'cell',
        'resizable-r': 'right',
        'resizable-b': 'bottom',
        'resizable-l': 'left',
        'resizable-t': 'top'
      },
      contextType: '',
      imgHeight: 0,
      imgWidth: 0,
      startMergeFlag: false,
      selectedCell: [],
      boundaryDataMap: {
        'lastCol': 0,
        'lastRow': 0,
        'firstRow': 0,
        'firstCol': 0
      }
    }
  },
  watch: {
    url(nv) {
      if (nv) {
        this.initImg()
      }
    },
    currentTop(nv) {
      this.resizeRow(nv, 'top')
    },
    currentLeft(nv) {
      this.resizeCol(nv, 'left')
    },
    currentWidth(nv) {
      // 拖动右框线
      if (this.currentLeft === this.offsetLeft) {
        this.resizeCol(this.currentItem.colStart * this.imgWidth + nv, 'right')
      }
    },
    currentHeight(nv) {
      // 拖动下框线
      if (this.currentTop === this.offsetTop) {
        this.resizeRow(this.currentItem.rowStart * this.imgHeight + nv, 'bottom')
      }
    },
    cols() {
      this.absoluteCols = [].concat(this.cols)
    },
    rows() {
      this.absoluteRows = [].concat(this.rows)
    },
    cells() {
      this.handleAbsoluteCellData()
    }
  },
  created() {
    document.addEventListener('click', () => {
      this.isShowContextMenu = false
      // this.selectedCell = []
    })
  },
  mounted() {
    // grid版本
    // this.handleCellData()
    // absolute版本
    // this.initData()
  },
  methods: {
    initData() {
      this.absoluteCols = [].concat(this.cols)
      this.absoluteRows = [].concat(this.rows)
      this.handleAbsoluteCellData()
    },
    initImg() {
      if (this.url) {
        // 获取图片宽高
        this.$nextTick(() => {
          const imgDom = this.$refs.innerImg
          imgDom.onload = () => {
            this.imgHeight = imgDom.height
            this.imgWidth = imgDom.width
            // 图片加载完之后加载框线
            this.initData()
          }
        })
      }
    },
    // handleCellData() {
    //   this.cellInfoList = []
    //   // 为配合cells从开始，row和col都增加一个0
    //   const cols = [0].concat(this.cols)
    //   const rows = [0].concat(this.rows)
    //   this.cells.forEach(item => {
    //     this.cellInfoList.push({
    //       cell: item,
    //       position: {
    //         colStart: cols[item[0] - 1],
    //         colEnd: cols[item[1] - 1],
    //         rowStart: rows[item[2] - 1],
    //         rowEnd: rows[item[3] - 1]
    //       }
    //     })
    //   })
    //   console.log('cellInfoList', this.cellInfoList)
    // },
    handleAbsoluteCellData() {
      this.cellInfoList = []
      this.selectedCell = []
      // 为配合cells从开始，row和col都增加一个0
      this.cells.forEach(item => {
        const colStart = this.absoluteCols[item.column_begin]
        const colEnd = this.absoluteCols[item.column_end]
        const rowStart = this.absoluteRows[item.row_begin]
        const rowEnd = this.absoluteRows[item.row_end]
        this.cellInfoList.push({
          cell: item,
          colStart,
          colEnd,
          rowStart,
          rowEnd
        })
      })
    },
    handleCellChange() {
      this.selectedCell = []
      const newList = _.cloneDeep(this.cellInfoList)
      const finalArr = []
      // 检查所有的cell是否符合标准(是否有部分重叠的格子和重复的格子)
      const rowMergeList = newList.filter(item => item.cell.row_end - item.cell.row_begin > 1).map(i => i.cell)
      const colMergeList = newList.filter(item => item.cell.column_end - item.cell.column_begin > 1).map(i => i.cell)
      this.cellInfoList = []
      newList.forEach(item => {
        const cell = item.cell
        const rowIndex = rowMergeList.findIndex(rowItem => (cell.column_begin === rowItem.column_begin && cell.column_end === rowItem.column_end) && ((cell.row_begin > rowItem.row_begin && cell.row_begin < rowItem.row_end) || (cell.row_end > rowItem.row_begin && cell.row_end < rowItem.row_end)))
        const colIndex = colMergeList.findIndex(colItem => (cell.row_begin === colItem.row_begin && cell.row_end === colItem.row_end) && ((cell.column_begin > colItem.column_begin && cell.column_begin < colItem.column_end) || (cell.column_end > colItem.column_begin && cell.column_end < colItem.column_end)))
        const sameItemIndex = finalArr.findIndex(sameItem => (cell.column_begin === sameItem.cell.column_begin) && (cell.row_begin === sameItem.cell.row_begin) && (cell.column_end === sameItem.cell.column_end) && (cell.row_end === sameItem.cell.row_end))
        // console.log('rowIndex, colIndex', rowIndex, colIndex, sameItemIndex, rowMergeList[rowIndex], item.cell)
        // console.log('this.absoluteCols', this.absoluteCols)
        if (rowIndex === -1 && colIndex === -1 && sameItemIndex === -1) {
          finalArr.push({
            cell: cell,
            colStart: this.absoluteCols[cell.column_begin],
            colEnd: this.absoluteCols[cell.column_end],
            rowStart: this.absoluteRows[cell.row_begin],
            rowEnd: this.absoluteRows[cell.row_end]
          })
        }
      })
      this.cellInfoList = finalArr
      // console.log('finalArr', finalArr)
      this.updateConfirmed()
    },
    resize() {
    },
    showContextMenu(event, item) {
      const className = event.srcElement.className
      let type = this.classNameMap[className]
      const selectedLength = this.selectedCell.length
      this.selectedCell = selectedLength > 1 ? this.selectedCell : [item.cell]
      // 点击外框，不能删除
      const isBorder = this.isClickBorder(type, item.cell)
      if (isBorder) {
        this.isShowContextMenu = false
        return
      }
      if (selectedLength > 1) {
        type = 'merge'
      }
      this.currentItem = item
      this.isShowContextMenu = true
      this.menuX = event.clientX
      this.menuY = event.clientY
      this.handleContextType(type)
    },
    handleMouseDown(event, item) {
      if (event.button === 0) {
        // 鼠标左键点击
        this.startMergeFlag = true
        this.selectedCell = []
        const index = this.findCellIndex(item.cell, this.selectedCell)
        // 添加节点
        if (index === -1) {
          // 找不到则添加
          this.selectedCell.push(item.cell)
        }
      }
    },
    handleMouseUp() {
      this.startMergeFlag = false
      // console.log('e move', e, item)
    },
    handleMouseMove(item) {
      // console.log('item', item)
      if (this.startMergeFlag) {
        const cell = item.cell
        const index = this.findCellIndex(cell, this.selectedCell)
        // 添加节点
        if (index === -1) {
          // 找不到则添加
          this.selectedCell.push(cell)
          this.handleSelecteCell()
        } else {
          // 找到则删除
          // this.selectedCell.splice(index, 1)
          this.handleDeleteCell(item)
        }
      }
    },
    handleSelecteCell() {
      const firstCell = this.selectedCell[0]
      const lastCell = this.selectedCell[this.selectedCell.length - 1]
      const lastRowEnd = lastCell.row_end
      const lastColEnd = lastCell.column_end
      const lastColBegin = lastCell.column_begin
      const lastRowBegin = lastCell.row_begin
      const firstRowBegin = firstCell.row_begin
      const firstColBegin = firstCell.column_begin
      const firstRowEnd = firstCell.row_end
      const firstColEnd = firstCell.column_end
      this.cellInfoList.forEach(item => {
        const arrIndex = this.findCellIndex(item.cell, this.selectedCell)
        const cell = item.cell
        const startRowIndex = cell.row_begin
        const endRowIndex = cell.row_end
        const startColIndex = cell.column_begin
        const endColIndex = cell.column_end
        // console.log('startRowIndex, lastRowEnd, endRowIndex, ', startRowIndex, lastRowEnd, endRowIndex)
        // console.log('startColIndex, lastColEnd, endColIndex', startColIndex, lastColEnd, endColIndex)
        if (arrIndex === -1) {
          if ((startRowIndex >= firstRowBegin) && (startColIndex >= firstColBegin) && (endColIndex <= lastColEnd) && (endRowIndex <= lastRowEnd)) {
            // 正向划选（划选路径为矩形）
            console.log('1')
            this.selectedCell.push(cell)
          } else if ((startRowIndex >= firstRowBegin) && (endRowIndex <= lastRowEnd) && (startColIndex < lastColEnd) && (endColIndex >= lastColEnd)) {
            // 正向划选（处理合并单元格对划选问题）
            this.boundaryDataMap = {
              lastCol: lastColEnd,
              lastRow: lastRowEnd,
              firstRow: firstRowBegin,
              firstCol: firstColBegin
            }
            this.selectedCell.push(cell)
            this.handleMergedCell(cell)
          } else if ((startColIndex >= firstColBegin) && (endColIndex <= lastColEnd) && (startRowIndex < lastRowEnd) && (endRowIndex >= lastRowEnd)) {
            this.selectedCell.push(cell)
          } else if ((endColIndex <= firstColBegin) && (endColIndex > lastColBegin) && (startRowIndex >= lastRowEnd) && (startRowIndex < firstRowEnd)) {
            // 反向L型划选
            this.selectedCell.push(cell)
          } else if ((startRowIndex >= lastRowBegin) && (startColIndex >= lastColEnd) && (endColIndex <= firstColEnd) && (endRowIndex <= firstRowBegin)) {
            this.selectedCell.push(cell)
          } else if ((startRowIndex >= firstRowEnd) && (endRowIndex <= lastRowEnd) && (startColIndex >= lastColEnd) && (endColIndex <= firstColEnd)) {
            this.selectedCell.push(cell)
          } else if ((startRowIndex >= lastRowEnd) && (endRowIndex <= firstRowEnd) && (startColIndex >= firstColEnd) && (endColIndex <= lastColEnd)) {
            this.selectedCell.push(cell)
          }
        }
      })
    },
    handleDeleteCell(selectedItem) {
      const currentCell = selectedItem.cell
      const currentRowEnd = currentCell.row_end
      const currentColEnd = currentCell.column_end
      // const currentRowBegin = currentCell.row_begin
      // const currentColBegin = currentCell.column_begin
      this.cellInfoList.forEach(item => {
        const arrIndex = this.findCellIndex(item.cell, this.selectedCell)
        const cell = item.cell
        const startRowIndex = cell.row_begin
        // const endRowIndex = cell.row_end
        const startColIndex = cell.column_begin
        // const endColIndex = cell.column_end
        // console.log('startRowIndex, lastRowEnd, endRowIndex, ', startRowIndex, lastRowEnd, endRowIndex)
        // console.log('startColIndex, lastColEnd, endColIndex', startColIndex, lastColEnd, endColIndex)
        if (arrIndex !== -1) {
          if (startRowIndex >= currentRowEnd) {
            this.selectedCell.splice(arrIndex, 1)
          }
          if (startColIndex >= currentColEnd) {
            this.selectedCell.splice(arrIndex, 1)
          }
          // if ((startRowIndex >= currentRowEnd) && (endColIndex <= currentColBegin)) {
          //   this.selectedCell.splice(arrIndex, 1)
          // }
          // if ((startColIndex >= currentColEnd) && (endRowIndex <= currentRowBegin)) {
          //   this.selectedCell.splice(arrIndex, 1)
          // }
        }
      })
    },
    handleMergedCell(cell) {
      if (cell.column_end > this.boundaryDataMap.lastCol) {
        // col右边超出
        this.handleColMergedCell(cell)
      }
      if (cell.row_end > this.boundaryDataMap.lastRow) {
        // row超出
        this.handleRowMergedCell(cell)
      }
      // if () {
      //   // col左边超出
      // }
    },
    handleColMergedCell(cell) {
      const addList = this.cellInfoList.filter(item => {
        const { column_end, column_begin, row_end, row_begin } = item.cell
        return (column_end <= cell.column_end) && (column_begin >= cell.column_begin) && (row_end <= this.boundaryDataMap.lastRow) && (row_begin >= this.boundaryDataMap.firstRow)
      })
      if (addList.length) {
        this.boundaryDataMap.lastCol = cell.column_end
        addList.forEach(item => {
          const arrIndex = this.findCellIndex(item.cell, this.selectedCell)
          if (arrIndex === -1) {
            this.selectedCell.push(item.cell)
            this.handleMergedCell(item.cell)
          }
        })
      }
    },
    handleRowMergedCell(cell) {
      const addList = this.cellInfoList.filter(item => {
        const { column_end, column_begin, row_end, row_begin } = item.cell
        return (column_end <= cell.column_end) && (column_begin >= cell.column_begin) && (row_end <= this.boundaryDataMap.lastRow) && (row_begin >= this.boundaryDataMap.firstRow)
      })
      if (addList.length) {
        this.boundaryDataMap.lastCol = cell.column_end
        addList.forEach(item => {
          const arrIndex = this.findCellIndex(item.cell, this.selectedCell)
          if (arrIndex === -1) {
            this.selectedCell.push(item.cell)
            this.handleMergedCell(item.cell)
          }
        })
      }
    },
    updateConfirmed() {
      this.$emit('updateConfirmed', false)
    },
    resizeMove(obj, item) {
      // console.log('obj', obj, item)
      this.startMergeFlag = false
      this.selectedCell = []
      this.currentTop = obj.top
      this.currentLeft = obj.left
      this.currentWidth = obj.width
      this.currentHeight = obj.height
      this.currentItem = item
      this.updateConfirmed()
    },
    resizeStart(obj) {
      this.startMergeFlag = false
      this.selectedCell = []
      this.offsetTop = obj.top
      this.offsetLeft = obj.left
      this.offestWidth = obj.width
      this.offestHeight = obj.height
    },
    resizeRow(offeset, direction) {
      if (direction === 'top') {
        // 移动上框线
        const index = this.currentItem.cell.row_begin
        this.absoluteRows[index] = offeset / this.imgHeight
      }
      if (direction === 'bottom') {
        // 移动下框线
        const index = this.currentItem.cell.row_end
        this.absoluteRows[index] = offeset / this.imgHeight
      }
      this.handleCellChange()
    },
    resizeCol(offeset, direction) {
      if (direction === 'left') {
        const index = this.currentItem.cell.column_begin
        this.absoluteCols[index] = offeset / this.imgWidth
      }
      if (direction === 'right') {
        const index = this.currentItem.cell.column_end
        this.absoluteCols[index] = offeset / this.imgWidth
      }
      this.handleCellChange()
    },
    // 判断当前点击是否为边框，即外框线
    isClickBorder(type, cell) {
      let flag = false
      const { column_begin, row_begin, column_end, row_end } = cell
      if (type === 'left' && column_begin === 0) {
        flag = true
      } else if (type === 'right' && (column_end === this.absoluteCols.length - 1)) {
        flag = true
      } else if (type === 'top' && row_begin === 0) {
        flag = true
      } else if (type === 'bottom' && (row_end === this.absoluteRows.length - 1)) {
        flag = true
      }
      return flag
    },
    // 区分右键点击类型并生成右键列表
    handleContextType(type) {
      // 生成右键列表
      if (type === 'cell') {
        // 添加行或列，或者split格子
        this.contextList = [
          {
            label: 'Add Row',
            value: 'addRow'
          },
          {
            label: 'Add Column',
            value: 'addCol'
          }
        ]
        const cell = this.currentItem.cell
        if ((cell.row_end - cell.row_begin > 1) || (cell.column_end - cell.column_begin > 1)) {
          // 拆分单元格
          this.contextList = [{
            label: 'Split',
            value: 'split'
          }]
        }
      } else if (type === 'left' || type === 'right') {
        // 删除列
        this.contextList = [
          {
            label: 'Delete Column',
            value: 'deleteCol'
          }
        ]
      } else if (type === 'bottom' || type === 'top') {
        // 删除行
        this.contextList = [
          {
            label: 'Delete Row',
            value: 'deleteRow'
          }
        ]
      } else if (type === 'merge') {
        this.contextList = [
          {
            label: 'Merge Cells',
            value: 'merge'
          }
        ]
      }
      this.contextType = type
    },
    calcMaxHeight(item) {
      let maxHeight = (item.rowEnd - item.rowStart) * this.imgHeight
      const startIndex = item.cell.row_begin
      const prevIndex = startIndex - 1
      const endIndex = item.cell.row_end
      if (startIndex !== 0) {
        // const nextIndex = endIndex === this.absoluteRows.length - 1 ? this.absoluteRows.length - 1 : endIndex + 1
        maxHeight = (this.absoluteRows[endIndex] - this.absoluteRows[prevIndex]) * this.imgHeight
      } else {
        maxHeight = (this.absoluteRows[endIndex] - 0) * this.imgHeight
      }
      return maxHeight
    },
    calcMaxWidth(item) {
      let maxWidth = (item.colEnd - item.colStart) * this.imgWidth
      const index = item.cell.column_begin
      const prevIndex = index - 1
      const endIndex = item.cell.column_end
      if (index !== 0) {
        // const nextIndex = index === this.absoluteCols.length - 1 ? this.absoluteCols.length - 1 : index + 1
        maxWidth = (this.absoluteCols[endIndex] - this.absoluteCols[prevIndex]) * this.imgWidth
      } else {
        maxWidth = (this.absoluteCols[endIndex] - 0) * this.imgWidth
      }
      return maxWidth
    },
    handleMenuClick(item) {
      switch (item.value) {
        case 'addRow':
          // 添加一行
          this.addRow()
          break
        case 'addCol':
          // 添加一列
          this.addCol()
          break
        case 'deleteCol':
          // 删除一列
          this.deleteCol()
          break
        case 'deleteRow':
          // 删除一行
          this.deleteRow()
          break
        case 'split':
          // 打散单元格为最小单位
          this.spiltCell()
          break
        case 'merge':
          // 合并单元格
          this.mergeCell()
      }
    },
    // 添加行
    addRow() {
      const startIndex = this.currentItem.cell.row_begin
      const endIndex = this.currentItem.cell.row_end
      const endItem = this.absoluteRows[endIndex]
      const startItem = this.absoluteRows[startIndex]
      const middleItem = (endItem - startItem) / 2 + startItem
      this.absoluteRows.splice(startIndex + 1, 0, middleItem)
      // 更改cell
      const newArr = []
      this.cellInfoList.forEach(item => {
        const cell = item.cell
        if (cell.row_begin > startIndex) {
          item.cell.row_begin = cell.row_begin + 1
          item.cell.row_end = cell.row_end + 1
          item.rowStart = this.absoluteRows[cell.row_begin + 1]
          item.rowEnd = this.absoluteRows[cell.row_end + 1]
        } else if ((cell.row_begin === startIndex) && (cell.row_end === endIndex)) {
          // 增加一行cell
          newArr.push({
            cell: {
              row_begin: startIndex,
              row_end: startIndex + 1,
              column_begin: cell.column_begin,
              column_end: cell.column_end
            },
            colStart: this.absoluteCols[cell.column_begin],
            colEnd: this.absoluteCols[cell.column_end],
            rowStart: this.absoluteRows[startIndex],
            rowEnd: this.absoluteRows[startIndex + 1]
          })
          // 之前的cell向下移
          item.cell.row_begin = cell.row_begin + 1
          item.cell.row_end = cell.row_end + 1
          item.rowStart = this.absoluteRows[cell.row_begin + 1]
          item.rowEnd = this.absoluteRows[cell.row_end + 1]
        } else if ((cell.row_begin <= startIndex) && (cell.row_end > startIndex)) {
          item.cell.row_end = cell.row_end + 1
          item.rowEnd = this.absoluteRows[cell.row_end + 1]
        }
        newArr.push(item)
      })
      this.cellInfoList = [].concat(newArr)
      this.handleCellChange()
    },
    // 添加列
    addCol() {
      const startIndex = this.currentItem.cell.column_begin
      const endIndex = this.currentItem.cell.column_end
      const endItem = this.absoluteCols[endIndex]
      const startItem = this.absoluteCols[startIndex]
      const middleItem = (endItem - startItem) / 2 + startItem
      this.absoluteCols.splice(startIndex + 1, 0, middleItem)
      // 更改cell
      const newArr = []
      this.cellInfoList.forEach(item => {
        const cell = item.cell
        if (cell.column_begin > startIndex) {
          item.cell.column_begin = cell.column_begin + 1
          item.cell.column_end = cell.column_end + 1
          item.colStart = this.absoluteCols[cell.column_begin + 1]
          item.colEnd = this.absoluteCols[cell.column_end + 1]
        } else if ((cell.column_begin === startIndex) && (cell.column_end === endIndex)) {
          // 增加一行cell
          newArr.push({
            cell: {
              column_begin: startIndex,
              column_end: startIndex + 1,
              row_begin: cell.row_begin,
              row_end: cell.row_end
            },
            colStart: this.absoluteCols[cell.startIndex],
            colEnd: this.absoluteCols[cell.startIndex + 1],
            rowStart: this.absoluteRows[cell.row_begin],
            rowEnd: this.absoluteRows[cell.row_end]
          })
          // 之前的cell向后移
          item.cell.column_begin = cell.column_begin + 1
          item.cell.column_end = cell.column_end + 1
          item.colStart = this.absoluteCols[cell.column_begin + 1]
          item.colEnd = this.absoluteCols[cell.column_end + 1]
        } else if ((cell.column_begin <= startIndex) && (cell.column_end > startIndex)) {
          item.cell.column_end = cell.column_end + 1
          item.colEnd = this.absoluteRows[cell.column_end + 1]
        }
        newArr.push(item)
      })
      this.cellInfoList = [].concat(newArr)
      this.handleCellChange()
    },
    // 删除列
    deleteCol() {
      let index
      if (this.contextType === 'left') {
        index = this.currentItem.cell.column_begin
      }
      if (this.contextType === 'right') {
        index = this.currentItem.cell.column_end
      }
      this.absoluteCols.splice(index, 1)
      console.log('absoluteCols', this.absoluteCols, this.currentItem)
      const newArr = []
      this.cellInfoList.forEach(item => {
        const cell = item.cell

        if (cell.column_begin >= index) {
          item.cell.column_begin = cell.column_begin - 1
          item.cell.column_end = cell.column_end - 1
          item.colStart = this.absoluteCols[cell.column_begin - 1]
          item.colEnd = this.absoluteCols[cell.column_end - 1]
        } else if ((cell.column_begin < index) && (cell.column_end > index)) {
          item.cell.column_end = cell.column_end - 1
          item.colEnd = this.absoluteCols[cell.column_end - 1]
        } else if ((cell.column_end - cell.column_begin > 1) && cell.column_end === index) {
          item.cell.column_end = cell.column_end - 1
          item.colEnd = this.absoluteCols[cell.column_end - 1]
        }
        newArr.push(item)
      })
      this.cellInfoList = [].concat(newArr)
      this.handleCellChange()
    },
    // 删除行
    deleteRow() {
      let index
      if (this.contextType === 'top') {
        index = this.currentItem.cell.row_begin
      }
      if (this.contextType === 'bottom') {
        index = this.currentItem.cell.row_end
      }
      this.absoluteRows.splice(index, 1)
      const newArr = []
      this.cellInfoList.forEach(item => {
        const cell = item.cell
        // const pushFlag = cell.row_end === index
        if (cell.row_begin >= index) {
          item.cell.row_begin = cell.row_begin - 1
          item.cell.row_end = cell.row_end - 1
          item.rowStart = this.absoluteRows[cell.row_begin - 1]
          item.rowEnd = this.absoluteRows[cell.row_end - 1]
        } else if ((cell.row_begin < index) && (cell.row_end > index)) {
          item.cell.row_end = cell.row_end - 1
          item.rowEnd = this.absoluteRows[cell.row_end - 1]
        } else if ((cell.row_end - cell.row_begin > 1) && cell.row_end === index) {
          item.cell.row_end = cell.row_end - 1
          item.rowEnd = this.absoluteRows[cell.row_end - 1]
        }
        newArr.push(item)
      })
      // this.cellInfoList.forEach(item => {
      //   const cell = item.cell
      //   if (cell.row_begin < rowLength) {
      //     if (cell.row_end > rowLength) {
      //       item.cell.row_end = rowLength
      //     }
      //     newArr.push(item)
      //   }
      // })
      this.cellInfoList = [].concat(newArr)
      this.handleCellChange()
    },
    spiltCell() {
      const startRowIndex = this.currentItem.cell.row_begin
      const endRowIndex = this.currentItem.cell.row_end
      const startColIndex = this.currentItem.cell.column_begin
      const endColIndex = this.currentItem.cell.column_end
      const rowGap = endRowIndex - startRowIndex
      const colGap = endColIndex - startColIndex
      if (rowGap * colGap > 1) {
        const newArr = []
        for (let i = 0; i < rowGap; i++) {
          for (let j = 0; j < colGap; j++) {
            const row_begin = startRowIndex + i
            const row_end = startRowIndex + i + 1
            const column_begin = startColIndex + j
            const column_end = startColIndex + j + 1
            newArr.push({
              cell: {
                row_begin,
                row_end,
                column_begin,
                column_end
              },
              colStart: this.absoluteCols[column_begin],
              colEnd: this.absoluteCols[column_end],
              rowStart: this.absoluteRows[row_begin],
              rowEnd: this.absoluteRows[row_end]
            })
          }
        }
        const index = this.cellInfoList.findIndex((item) => {
          const { row_begin, row_end, column_begin, column_end } = item.cell
          return (startRowIndex === row_begin) && (endRowIndex === row_end) && (startColIndex === column_begin) && (endColIndex === column_end)
        })
        this.cellInfoList.splice(index, 1)
        this.cellInfoList = this.cellInfoList.concat(newArr)
        this.handleCellChange()
      }
      // 更新cell
      // const newArr = []
      // const endItem = this.absoluteRows[endIndex]
      // const startItem = this.absoluteRows[startIndex]
      // const middleItem = (endItem - startItem) / 2 + startItem
      // this.absoluteRows.splice(startIndex + 1, 0, middleItem)
      // // 更改cell
      // const newArr = []
      // this.cellInfoList.forEach(item => {
      //   const cell = item.cell
      //   if (cell.row_begin > startIndex) {
      //     item.cell.row_begin = cell.row_begin + 1
      //     item.cell.row_end = cell.row_end + 1
      //     item.rowStart = this.absoluteRows[cell.row_begin + 1]
      //     item.rowEnd = this.absoluteRows[cell.row_end + 1]
      //   } else if (cell.row_begin === startIndex) {
      //     // 增加一行cell
      //     newArr.push({
      //       cell: {
      //         row_begin: startIndex,
      //         row_end: startIndex + 1,
      //         column_begin: cell.column_begin,
      //         column_end: cell.column_end
      //       },
      //       colStart: this.absoluteCols[cell.column_begin],
      //       colEnd: this.absoluteCols[cell.column_end],
      //       rowStart: this.absoluteRows[startIndex],
      //       rowEnd: this.absoluteRows[startIndex + 1]
      //     })
      //     // 之前的cell向下移
      //     item.cell.row_begin = cell.row_begin + 1
      //     item.cell.row_end = cell.row_end + 1
      //     item.rowStart = this.absoluteRows[cell.row_begin + 1]
      //     item.rowEnd = this.absoluteRows[cell.row_end + 1]
      //   }
      //   newArr.push(item)
      // })
      // this.cellInfoList = [].concat(newArr)
      // this.handleCellChange()
      // console.log('cellInfoList', this.cellInfoList)
    },
    mergeCell() {
      let max_row_end = this.selectedCell[0].row_end
      let max_row_begin = this.selectedCell[0].row_begin
      let max_column_end = this.selectedCell[0].column_end
      let max_column_begin = this.selectedCell[0].column_begin
      const newSelectedCell = []
      this.selectedCell.forEach(item => {
        max_row_end = item.row_end >= max_row_end ? item.row_end : max_row_end
        max_row_begin = item.row_begin <= max_row_begin ? item.row_begin : max_row_begin
        max_column_end = item.column_end >= max_column_end ? item.column_end : max_column_end
        max_column_begin = item.column_begin < max_column_begin ? item.column_begin : max_column_begin
      })
      console.log('max_row_begin, max_row_end, max_column_begin, max_column_bend', max_row_begin, max_row_end, max_column_begin, max_column_end)
      this.cellInfoList.forEach(item => {
        const cell = item.cell
        if ((cell.row_end <= max_row_end) && (cell.row_begin >= max_row_begin) && (cell.column_end <= max_column_end) && (cell.column_begin >= max_column_begin)) {
          newSelectedCell.push(cell)
        }
      })
      newSelectedCell.forEach(cell => {
        const index = this.cellInfoList.findIndex((item) => {
          const { row_begin, row_end, column_begin, column_end } = item.cell
          return (cell.row_begin === row_begin) && (cell.row_end === row_end) && (cell.column_begin === column_begin) && (cell.column_end === column_end)
        })
        this.cellInfoList.splice(index, 1)
      })
      console.log('111')
      this.cellInfoList.push({
        cell: {
          column_begin: max_column_begin,
          column_end: max_column_end,
          row_begin: max_row_begin,
          row_end: max_row_end
        },
        colStart: this.absoluteCols[max_column_begin],
        colEnd: this.absoluteCols[max_column_end],
        rowStart: this.absoluteRows[max_row_begin],
        rowEnd: this.absoluteRows[max_row_end]
      })
      console.log('max_column_begin 1', max_column_begin, max_column_end, max_row_end, max_row_begin)
      this.handleCellChange()
      this.selectedCell = []
    },
    findCellIndex(cell, arr) {
      const startRowIndex = cell.row_begin
      const endRowIndex = cell.row_end
      const startColIndex = cell.column_begin
      const endColIndex = cell.column_end
      const index = arr.findIndex((item) => {
        const { row_begin, row_end, column_begin, column_end } = item
        return (startRowIndex === row_begin) && (endRowIndex === row_end) && (startColIndex === column_begin) && (endColIndex === column_end)
      })
      return index
    }
  }
}
</script>
<style lang="less">
.vdr, .vdr.active:before {
  position: relative;
}
.vdr {
  border: 1px solid #000;
}
.resizable-component {
  .resizable-t {
    height: 2px !important;
    top: -2px !important;
  }
  .resizable-b {
    height: 2px !important;
    bottom: -2px !important;
  }
  .resizable-r {
    width: 2px !important;
    right: -2px !important;
  }
  .resizable-l {
    width: 2px !important;
    left: -2px !important;
  }
}
</style>
<style lang="less" scoped>
.demo-list {
  display: grid;
  margin-top: 48px;
  width: 500px;
  height: 500px;
  // grid-template-columns: 20% 30% 50%;
  // grid-template-rows: 30% 30% 40%;
}
.table-cell {
  border-top: 1px solid red;
  border-right: 1px solid red;
}
.demo-list {
  border-bottom: 1px solid red;
  border-left: 1px solid red;
}
.position-container {
  position: relative;
  width: 100%;
  // height: 500px;
  // background: forestgreen;
  // border-bottom: 1px solid red;
  // border-left: 1px solid red;
  .resizable-component {
    position: absolute;
    border: 1px solid red;
    // border-right: 1px solid red;
  }
}
.context-menu {
  position: fixed;
  z-index:2000;
  padding: 6px 0;
  background: #fff;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  border-radius: 4px;
  border: 1px solid #e6ebf5;
  .menu-item {
    padding: 8px 20px;
    width: 150px;
    text-align: center;
    font-size: 14px;
    &:hover {
      background: #eee;
      cursor: pointer;
    }
    &.active-item {
      color: #007cc4;
      font-weight: 500;
    }
  }
}
</style>
