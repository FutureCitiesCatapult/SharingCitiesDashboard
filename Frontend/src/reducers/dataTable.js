import {
  FETCH_ATTRIBUTE_DATA,
  FETCH_ATTRIBUTE_DATA_FULFILLED,
  FETCH_ATTRIBUTE_DATA_REJECTED,
  FETCH_ATTRIBUTES,
  FETCH_ATTRIBUTES_FULFILLED,
  FETCH_ATTRIBUTES_REJECTED,
  FETCH_SUBTHEMES,
  FETCH_SUBTHEMES_FULFILLED,
  FETCH_SUBTHEMES_REJECTED,
  FETCH_THEMES,
  FETCH_THEMES_FULFILLED,
  FETCH_THEMES_REJECTED,
  QUERY_PARAMS,
  REMOVE_ATTRIBUTE_DATA,
  RESET_STATE,
  SET_ACTIVE_TAB_ATTRIBUTE,
  TOGGLE_ATTRIBUTE_SELECTED,
  TOGGLE_SUBTHEME_SELECTED,
  TOGGLE_THEME_SELECTED,
  EXPORT_DATA,
  EXPORT_DATA_REJECTED,
  EXPORT_DATA_FULFILLED
} from "../constants";

const FCC_CONFIG = require('./../../fcc.config');

const initialState = {
  themes: [],
  queryParams: {
    grouped: null,
    per_sensor: null,
    harmonising_method: QUERY_PARAMS.HARMONISING_METHOD_LONG,
    limit: 100,
  },
  data: [],
  activeTabAttribute: null,
  fetching: false,
  fetched: false,
  error: null,
};

export default (state=initialState, action={}) => {
  switch (action.type) {

    case FETCH_THEMES: {
      return {
        ...state,
        fetching: true,
      }
    }

    case FETCH_THEMES_FULFILLED: {
      return {
        ...state,
        fetching: false,
        fetched: true,
        themes: action.payload.map(theme => ({
          id: theme.id,
          name: theme.Name,
          subthemes: [],
          isSelected: false,
        }))
      }
    }

    case FETCH_THEMES_REJECTED: {
      return {
        ...state,
        fetching: false,
        fetched: false,
        error: action.payload,
      }
    }

    case TOGGLE_THEME_SELECTED: {
      const newThemes = [...state.themes];

      const themeToToggle = newThemes.find(theme => theme.id === action.payload);
      themeToToggle.isSelected = !themeToToggle.isSelected;

      return {
        ...state,
        themes: newThemes,
      }
    }

    case FETCH_SUBTHEMES: {
      return {
        ...state,
        fetching: true,
      }
    }

    case FETCH_SUBTHEMES_FULFILLED: {
      const newThemes = [...state.themes];

      newThemes.find(theme => theme.id === action.payload.themeId).subthemes = action.payload.subthemes.map(subtheme => ({
        id: subtheme.id,
        name: subtheme.Name,
        attributes: [],
        isSelected: false,
      }));

      return {
        ...state,
        fetching: false,
        fetched: true,
        themes: newThemes,
      }
    }

    case FETCH_SUBTHEMES_REJECTED: {
      return {
        ...state,
        fetching: false,
        fetched: false,
        error: action.payload,
      }
    }

    case TOGGLE_SUBTHEME_SELECTED: {
      const newThemes = [...state.themes];
      const parentTheme = newThemes.find(theme => theme.id === action.payload.themeId);

      const subthemeToToggle = parentTheme.subthemes.find(subtheme => subtheme.id === action.payload.subthemeId);
      subthemeToToggle.isSelected = !subthemeToToggle.isSelected;

      return {
        ...state,
        themes: newThemes,
      }
    }

    case FETCH_ATTRIBUTES: {
      return {
        ...state,
        fetching: true,
      }
    }

    case FETCH_ATTRIBUTES_FULFILLED: {
      const newThemes = [...state.themes];
      const parentTheme = newThemes.find(theme => theme.id === action.payload.themeId);

      const parentSubtheme = parentTheme.subthemes.find(subtheme => subtheme.id === action.payload.subthemeId);
      parentSubtheme.attributes = action.payload.attributes.map(attribute => {
        return {
          id: attribute.id,
          name: attribute.name,
          tableName: attribute['table_name'],
          subthemeId: attribute['Sub Theme id'],
          unit: attribute['Unit'],
          unitValue: attribute['Unit Value'],
          description: attribute['Description'],
          isSelected: false,
        }
      });

      return {
        ...state,
        fetching: false,
        fetched: true,
        themes: newThemes,
      }
    }

    case FETCH_ATTRIBUTES_REJECTED: {
      return {
        ...state,
        fetching: false,
        fetched: false,
        error: action.payload,
      }
    }

    case TOGGLE_ATTRIBUTE_SELECTED: {
      const updatedThemes = [...state.themes];

      const attributeToToggle = updatedThemes
        .find((theme) => theme.id === action.payload.themeId).subthemes
        .find((subtheme) => subtheme.id === action.payload.subthemeId).attributes
        .find((attr) => attr.id === action.payload.attributeId);
      attributeToToggle.isSelected = !attributeToToggle.isSelected;

      return {
        ...state,
        themes: updatedThemes,
      }
    }

    case FETCH_ATTRIBUTE_DATA: {
      return {
        ...state,
        fetching: true,
      }
    }

    case FETCH_ATTRIBUTE_DATA_FULFILLED: {
      return {
        ...state,
        fetching: false,
        fetched: true,
        data: [...state.data, ...action.payload.data],
        queryParams: {
          ...state.queryParams,
          ...action.payload.queryParams,
        }
      }
    }

    case FETCH_ATTRIBUTE_DATA_REJECTED: {
      return {
        ...state,
        fetching: false,
        fetched: false,
        error: action.payload,
      }
    }

    case REMOVE_ATTRIBUTE_DATA: return ({
      ...state,
      data: [...state.data].filter(attr => attr['Attribute_id'] !== action.payload),
    });

    case RESET_STATE: {
      return initialState
    }

    case SET_ACTIVE_TAB_ATTRIBUTE: return ({
      ...state,
      activeTabAttribute: action.payload,
    })

  }

  return state
}