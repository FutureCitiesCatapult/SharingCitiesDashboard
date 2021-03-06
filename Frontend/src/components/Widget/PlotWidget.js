import React from 'react';
import PropTypes from 'prop-types';
import {
  Fade,
  withStyles,
} from '@material-ui/core';
import VegaLite from 'react-vega-lite';
import { Handler } from 'vega-tooltip';
import axios from 'axios';
import WidgetWrapper from './WidgetWrapper';
import LoadingIndicator from './LoadingIndicator';
import ContainerDimensions from 'react-container-dimensions'

const FCC_CONFIG = require('./../../../fcc.config');

const styles = (theme) => ({
  root: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: 'inherit',
    width: 'inherit',
    marginTop: -theme.spacing.unit * 3,
  },
});

const tooltipOptions = {
  theme: 'custom',
  styleId: 'customTooltip',
};

class PlotWidget extends React.Component {
  static propTypes = {
    classes: PropTypes.object.isRequired,
    theme: PropTypes.object.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    width: PropTypes.number.isRequired,
    height: PropTypes.number.isRequired,
    w: PropTypes.number.isRequired,
    h: PropTypes.number.isRequired,
    isStatic: PropTypes.bool.isRequired,
    type: PropTypes.string.isRequired,
    config: PropTypes.object.isRequired,
    queryParams: PropTypes.object.isRequired,
  };

  constructor(props) {
    super(props);

    const { theme, config, width, height, w, h } = this.props;

    const titleTypography = theme.typography.body1;
    const labelTypography = theme.typography.body2;

    this.state = {
      loading: null,
      error: null,
      data: null,
      spec: {
        ...config.spec,
        width: width,
        height: height,
        w: w,
        h: h,
        config: {
          axis: {
            // x & y axis lines
            domainColor: theme.palette.primary.main,

            // grid
            gridColor: theme.palette.primary.main,

            // x & y axis labels
            labelColor: theme.palette.primary.main,
            labelFont: labelTypography.fontFamily,
            labelFontSize: parseFloat(labelTypography.fontSize) * theme.typography.fontSize,
            labelFontWeight: labelTypography.fontWeight,

            // axis titles
            titleColor: titleTypography.color,
            titleFont: titleTypography.fontFamily,
            titleFontSize: parseFloat(titleTypography.fontSize) * theme.typography.fontSize,
            titleFontWeight: titleTypography.fontWeight,
            titlePadding: theme.spacing.unit,

            tickColor: theme.palette.primary.main,
          },
          legend: {
            titleColor: titleTypography.color,
            titleFont: titleTypography.fontFamily,
            titleFontSize: parseFloat(titleTypography.fontSize) * theme.typography.fontSize,
            titleFontWeight: titleTypography.fontWeight,

            labelColor: theme.palette.primary.main,
            labelFont: labelTypography.fontFamily,
            labelFontSize: parseFloat(labelTypography.fontSize) * theme.typography.fontSize,
            labelFontWeight: labelTypography.fontWeight,
          },

          title: {
            color: theme.palette.primary.main,
            font: labelTypography.fontFamily,
            fontSize: parseFloat(labelTypography.fontSize) * theme.typography.fontSize,
            fontWeight: labelTypography.fontWeight,
          },
        },
      },
    };

    this.tooltipHandler = new Handler(tooltipOptions)
  }

  componentWillMount() {
    this.fetchData()
  }

  fetchData = () => {
    const { queryParams } = this.props;

    this.setState({ loading: true });

    axios({
      url: FCC_CONFIG.apiRoot + '/data',
      method: 'get',
      params: queryParams,
    })
      .then((response) => {
        this.setState({
          loading: false,
          data: {
            values: response.data,
          }
        })
      })
      .catch((err) => {
        this.setState({ error: err})
      })
  };

  render() {
    const { classes, i, type, name, description, isStatic, width, height, w, h, config, queryParams } = this.props;
    const { spec, loading, error, data } = this.state;

    if (!data) {
      return (
        <WidgetWrapper
          i={i}
          type={type}
          name={name}
          description={description}
          isStatic={isStatic}
          width={width}
          height={height}
          w={w}
          h={h}
          config={config}
          queryParams={queryParams}
        >
          <LoadingIndicator />
        </WidgetWrapper>
      )
    }

    return (
      <WidgetWrapper
        i={i}
        type={type}
        name={name}
        description={description}
        isStatic={isStatic}
        width={width}
        height={height}
        w={w}
        h={h}
        config={config}
        queryParams={queryParams}
      >
        <Fade in={!loading} mountOnEnter>
          <ContainerDimensions>
            {({ width, height }) => {
              const responsiveSpec = { ...spec, width: Math.floor(width), height: Math.floor(height) - 100 }
              return <VegaLite
                className={classes.root}
                spec={responsiveSpec}
                data={data}
                tooltip={this.tooltipHandler.call}
              />
            }}
          </ContainerDimensions>
        </Fade>
      </WidgetWrapper>
    )
  }
}

PlotWidget = withStyles(styles, { withTheme: true })(PlotWidget);

export default PlotWidget
