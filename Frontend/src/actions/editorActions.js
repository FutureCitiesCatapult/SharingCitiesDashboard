import {
  PURGE_EDITOR,
  SET_MAP_CAN_MAP,
  SET_MAP_CENTER,
  SET_MAP_DATA,
  SET_MAP_TILE_LAYER,
  SET_MAP_ZOOM,
  SET_PLOT_DATA,
  SET_PLOT_DESCRIPTION,
  SET_PLOT_ENCODING,
  SET_PLOT_TYPE,
  SET_WIDGET_NAME,
  SET_WIDGET_TYPE,
} from "./../constants";

const canMap = record => {
  const requiredKeys = ['lat', 'lon'];
  const presentKeys = Object.keys(record);

  for (let rk of requiredKeys) {
    if (!presentKeys.includes(rk)) return false;
  }

  return true
};

export function initializeEditor() {

  // ToDo :: this needs to remember stuff rather than jusyt overwrite it every time

  return function(dispatch, getState) {
    const currentState = getState();
    const defaults = currentState.config.config.widgetEditorDefaults;
    const data = currentState.data.data;
    const nonNumericColumns = currentState.data.meta.columns.filter(column => !column.numeric);
    const numericColumns = currentState.data.meta.columns.filter(column => column.numeric);

    dispatch({
      type: SET_WIDGET_NAME,
      payload: defaults.widgetName,
    });

    dispatch({
      type: SET_WIDGET_TYPE,
      payload: defaults.widgetType,
    });

    dispatch({
      type: SET_PLOT_TYPE,
      payload: defaults.plotType,
    });

    dispatch({
      type: SET_PLOT_DATA,
      payload: data,
    });

    dispatch({
      type: SET_PLOT_ENCODING,
      payload: {
        axis: "x",
        field: nonNumericColumns[0].id,
        type: "ordinal",
      }
    });

    dispatch({
      type: SET_PLOT_ENCODING,
      payload: {
        axis: "y",
        field: numericColumns[0].id,
        type: "quantitative",
      }
    });

    dispatch({
      type: SET_MAP_TILE_LAYER,
      payload: defaults.mapTileLayer,
    });

    dispatch({
      type: SET_MAP_CAN_MAP,
      payload: canMap(data[0])
    });

    dispatch({
      type: SET_MAP_DATA,
      payload: data,
    });

    dispatch({
      type: SET_MAP_ZOOM,
      payload: defaults.mapZoom,
    });

    dispatch({
      type: SET_MAP_CENTER,
      payload: defaults.mapCenter,
    });
  }
}

export function purgeEditor() {
  return {
    type: PURGE_EDITOR,
  }
}

export function setMapTileLayer(tileLayer) {
  return {
    type: SET_MAP_TILE_LAYER,
    payload: tileLayer,
  }
}

export function setMapCenter(center) {
  return {
    type: SET_MAP_CENTER,
    payload: center,
  }
}

export function setMapZoom(zoom) {
  return {
    type: SET_MAP_ZOOM,
    payload: zoom,
  }
}

export function setPlotDescription(desc = '') {
  return {
    type: SET_PLOT_DESCRIPTION,
    payload: desc,
  }
}

export function setPlotEncoding(enc = {}) {
  return {
    type: SET_PLOT_ENCODING,
    payload: enc,
  }
}

export function setPlotType(type) {
  return {
    type: SET_PLOT_TYPE,
    payload: type,
  }
}

export function setWidgetName(name = '') {
  return {
    type: SET_WIDGET_NAME,
    payload: name,
  }
}

export function setWidgetType(type) {
  return {
    type: SET_WIDGET_TYPE,
    payload: type,
  }
}
