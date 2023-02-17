<template>
  <div class="file-table-container">
    <el-row v-loading="loading && (fileImgList.length !== imgLoadLength ) && imgLoadLength !== 0" type="flex">
      <el-col :span="12" class="layout-left">
        <VuePerfectScrollbar style="padding: 0 36px;">
          <LeftPanel :outline-update-res="outlineUpdateRes" @selectTable="getTableOutline" @fileImgList="getFileImgList" @imgLoadLength="getImgLoadLength" @getLoading="getLoading" @fileId="getFileId" />
        </VuePerfectScrollbar>
      </el-col>
      <el-col :span="12" class="layout-right">
        <VuePerfectScrollbar style="padding: 0 36px;">
          <RightPanel :select-table="selectTable" @saveSuccess="updateOutlineSuccess" :fileId="fileId" />
        </VuePerfectScrollbar>
      </el-col>
    </el-row>
  </div>
</template>
<script>
import RightPanel from './RightPanel'
import LeftPanel from './LeftPanel'
import VuePerfectScrollbar from 'vue-perfect-scrollbar'
export default {
  components: { RightPanel, LeftPanel, VuePerfectScrollbar },
  props: {
    pdfUrl: {
      type: String,
      default: () => ''
    }
  },
  data() {
    return {
      selectTable: {},
      fileImgList: [],
      outlineUpdateRes: 0,
      imgLoadLength: -1,
      loading: false,
      fileId: ''
    }
  },
  methods: {
    getTableOutline(data) {
      this.selectTable = data
    },
    getFileImgList(data) {
      this.fileImgList = data
    },
    updateOutlineSuccess(data) {
      this.outlineUpdateRes = data
    },
    getImgLoadLength(data) {
      this.imgLoadLength = data
    },
    getLoading(data) {
      this.loading = data
    },
    getFileId(data) {
      this.fileId = data
      console.log('data fileid', data)
    }
  }
}
</script>
<style lang="less" scoped>
  .layout-left, .layout-right {
    // min-height: calc(100vh - 64px);
    height: calc(100vh - 64px) !important;
    padding: 36px 24px;
    background: #f3f3f3;
  }
  .layout-left {
    border-right: 1px solid #000;
  }
  .file-table-container, .el-row, .el-col, .ps {
    height: 100%;
  }
  .el-progress {
    position: absolute;
    left: calc(50% - 63px);
    top: calc(50% - 63px);
  }
</style>
