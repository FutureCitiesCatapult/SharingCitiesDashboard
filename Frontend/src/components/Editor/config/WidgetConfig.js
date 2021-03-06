import React from 'react';
import PropTypes from 'prop-types';
import {
  Divider,
  FormControl,
  FormControlLabel,
  FormGroup,
  FormHelperText,
  Switch,
  TextField,
  withStyles,
  Typography
} from '@material-ui/core';
import { connect } from 'react-redux';
import { setWidgetProperty } from './../../../actions/editorActions';

const styles = (theme) => ({
  root: {
    flexDirection: 'column',
    padding: theme.spacing.unit,
  },
});

class WidgetConfig extends React.Component {
  static propTypes = {
    classes: PropTypes.object.isRequired,
    editor: PropTypes.object.isRequired,
    setWidgetProperty: PropTypes.func.isRequired,
  };

  setWidgetProperty = (property) => (e) => {
    this.props.setWidgetProperty(property, e.target.value)
  };

  setWidgetStatic = (e) => {
    this.props.setWidgetProperty('isStatic', e.target.checked)
  };

  render() {
    const { classes, editor } = this.props;

    return (
      <FormGroup className={classes.root}>
        <FormControl htmlFor="widget-name">
          <TextField
            id="widget-name"
            label="Name"
            value={editor.widget.name}
            onChange={this.setWidgetProperty('name')}
            margin="normal"
          />
        </FormControl>
        <FormControl htmlFor="widget-description">
          <TextField
            id="widget-description"
            label="Description"
            value={editor.widget.description}
            onChange={this.setWidgetProperty('description')}
            margin="normal"
            multiline={true}
            rows={3}
          />
        </FormControl>
        {/*Hide width option on edit mode*/}
        {editor.mode === 'add' ? <FormControl htmlFor="widget-width">
          <TextField
            id="widget-width"
            label="Width (columns)"
            value={editor.widget.w}
            onChange={this.setWidgetProperty('w')}
            margin="normal"
          />
          {editor.widget.w < 4 || editor.widget.w > 12 ? <Typography color="error">A value between 4 and 12 is advised</Typography> : null}
        </FormControl> : null}
        {/*Hide height option on edit mode*/}
        {editor.mode === 'add' ? <FormControl htmlFor="widget-height">
            <TextField
              id="widget-height"
              label="Height (rows)"
              value={editor.widget.h}
              onChange={this.setWidgetProperty('h')}
              margin="normal"
            />
            {editor.widget.h > 15 || editor.widget.h < 8 ? <Typography color="error">A value between 8 and 15 is advised</Typography> : null}
        </FormControl> : null}
        <FormGroup row>
          <FormControlLabel
            label="Static"
            control={
              <Switch
                checked={editor.widget.isStatic}
                onChange={this.setWidgetStatic}
                value={editor.widget.isStatic}
                color="primary"
              />
            }
          />
        </FormGroup>
        <FormHelperText>If static is set the widget cannot be moved around the dashboard</FormHelperText>
      </FormGroup>
    )
  }
}

const mapStateToProps = (state) => ({
  editor: state.editor,
});

const mapDispatchToProps = (dispatch) => ({
  setWidgetProperty: (property, value) => dispatch(setWidgetProperty(property, value)),
});

WidgetConfig = withStyles(styles)(WidgetConfig);
WidgetConfig = connect(mapStateToProps, mapDispatchToProps)(WidgetConfig);

export default WidgetConfig
