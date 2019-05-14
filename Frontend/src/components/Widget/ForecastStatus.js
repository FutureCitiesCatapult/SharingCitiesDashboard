import React from 'react';
import PropTypes from 'prop-types';
import {
  Typography,
  withStyles,
} from '@material-ui/core';
import TimeIcon from '@material-ui/icons/AccessTime';

const styles = (theme) => ({
  root: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'column',
    height: '75%',
    padding: theme.spacing.unit * 4,
  },
  progress: {
    margin: theme.spacing.unit * 2,
  },
  pendingIcon: {
    margin: theme.spacing.unit * 2,
    color: theme.palette.secondary.main,
    fontSize: 46
  }
});

const ForecastStatus = (props) => {
  const { classes, forecast } = props;

  return (
    <div className={classes.root}>
      <TimeIcon className={classes.pendingIcon}/>
      <Typography variant="subtitle1" color="primary">
        Status: { forecast.state }
      </Typography>
      <Typography variant="caption" color="primary">
        {forecast.status}
      </Typography>
    </div>
  );
};

ForecastStatus.propTypes = {
  classes: PropTypes.object.isRequired,
  forecast: PropTypes.object.isRequired,
};

export default withStyles(styles)(ForecastStatus)
