import React, { useCallback, useEffect, useMemo, useRef } from "react"

import { Streamlit } from "streamlit-component-lib"
import { useStreamlit } from "streamlit-component-lib-react-hooks"

import { VTKViewer, VTKViewerDrawer, VTKFloatingToolbar } from "lavender-vtkjs"

import { Layout, notification } from "antd"

import './VTKStreamlit.css'

// compare TypedArrays
// https://stackoverflow.com/questions/21553528/how-to-test-for-equality-in-arraybuffer-dataview-and-typedarray
const compareTypedArrays: (a: Uint8Array, b: Uint8Array) => boolean = (a, b) => {
  if (a.byteLength !== b.byteLength) return false;
  return a.every((val, i) => val === b[i]);
}

const VTKStreamlit: React.FunctionComponent = () => {
  const viewerRef = useRef<any>(null)
  const clearRef = useRef<boolean>(true)

  const renderData = useStreamlit()

  const [viewerState, setViewerState] = React.useState<any>({})

  const [file, setFile] = React.useState<Uint8Array | undefined>(undefined)

  const initialLoad = useRef(true)

  useEffect(() => {
    if (renderData && typeof renderData.args["clear"] !== undefined) {
      clearRef.current = renderData.args["clear"]
    }
  }, [renderData])

  useEffect(() => {
    if (renderData && renderData.args["file"]) {
      setFile(currFile => {
        if (!currFile) return renderData.args["file"]
        const equal = compareTypedArrays(renderData.args["file"], currFile)
        return equal ? currFile : renderData.args["file"]
      })
    }
  }, [renderData])

  const loadFile = useCallback((file: Uint8Array) => {
    const config = initialLoad.current ? undefined : viewerState
    initialLoad.current = false
    viewerRef.current.loadFile(new Blob([file]), 'vtkjs', config)
  }, [viewerState])

  useEffect(() => {
    if (!file) return
    if (viewerRef.current && viewerRef.current.loadFile) {
      if (clearRef.current) viewerRef.current.dispatch({ type: 'remove-all', skipRender: true })
      loadFile(file)
      if (clearRef.current) viewerRef.current.dispatch({ type: 'reset-camera' })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [file])

  const toolbar = useMemo(() => {
    if (renderData && typeof renderData.args["toolbar"] !== 'undefined') {
      return renderData.args["toolbar"]
    }
    else {
      return true
    }
  }, [renderData])

  const sider = useMemo(() => {
    if (renderData && typeof renderData.args["sider"] !== 'undefined') {
      return renderData.args["sider"]
    }
    else {
      return true
    }
  }, [renderData])

  const cssStyle = useMemo(() => {
    if (renderData && typeof renderData.args["style"] !== 'undefined') {
      if (renderData.args["style"].height && renderData.args["style"].height.includes('px')) {
        Streamlit.setFrameHeight(parseInt(renderData.args["style"].height.replace('px', '')))
      }
      return renderData.args["style"]
    }
    else {
      return { border: "1px solid #d0d7de", borderRadius: "2px" }
    }
  }, [renderData])

  useEffect(() => {
    Streamlit.setComponentValue(viewerState)
  }, [viewerState])

  const handleScreenshot = () => {
    if (!viewerRef.current) return
    viewerRef.current.handleScreenshot('VTKJSStreamlit')
      .then(() => {
        notification.success({
          message: `Copied to Clipboard`,
          placement: 'topRight',
        });
      })
  }

  if (renderData == null) {
    return null
  }

  return (
    <div style={{ width: '100%', height: '100%', border: "1px solid #d0d7de", borderRadius: "2px", ...cssStyle, display: 'flex' }}>
      <Layout style={{ flexDirection: 'row' }}>
        {sider &&
          <VTKViewerDrawer dispatch={viewerRef.current?.dispatch} viewerState={viewerState} handleScreenshot={handleScreenshot} />
        }
        <Layout>
          {toolbar &&
            <VTKFloatingToolbar dispatch={viewerRef.current?.dispatch} viewerState={viewerState} handleScreenshot={handleScreenshot} />
          }
          <Layout.Content style={{ display: 'flex', flexDirection: 'column' }}>
            <VTKViewer setViewerState={setViewerState} ref={viewerRef} />
          </Layout.Content>
        </Layout>
      </Layout>
    </div>
  )
}

export default VTKStreamlit