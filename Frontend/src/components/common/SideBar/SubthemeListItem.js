import React from 'react';
import PropTypes from 'prop-types';

import AttributeList from './AttributeList';

// material-ui
import { withStyles } from '@material-ui/core/styles';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import RadioButtonUncheckedIcon from '@material-ui/icons/RadioButtonUnchecked';
import RadioButtonCheckedIcon from '@material-ui/icons/RadioButtonChecked';
import Collapse from '@material-ui/core/Collapse';

const styles = (theme) => ({
  nested: {
    paddingLeft: theme.spacing.unit * 4,
  },
  darkColor: {
    color: theme.palette.primary.dark,
  },
});

class SubthemeListItem extends React.Component {
  handleClick = () => {
    this.props.onClick();
  };

  render() {
    const { classes, subthemeId, subthemeName, themeId, isSelected } = this.props;

    return (
      <React.Fragment>
        <ListItem button className={classes.nested} onClick={this.handleClick}>
          {
            isSelected
              ? <RadioButtonCheckedIcon fontSize="small" color="secondary" />
              : <RadioButtonUncheckedIcon fontSize="small" className={classes.darkColor} />
          }
          <ListItemText inset primary={subthemeName} />
        </ListItem>
        <Collapse in={isSelected} timeout="auto" unmountOnExit>
          <AttributeList
            themeId={themeId}
            subthemeId={subthemeId}
          />
        </Collapse>
      </React.Fragment>
    )
  }
}

SubthemeListItem.propTypes = {
  classes: PropTypes.object.isRequired,
  themeId: PropTypes.number.isRequired,
  subthemeId: PropTypes.number.isRequired,
  subthemeName: PropTypes.string.isRequired,
  isSelected: PropTypes.bool.isRequired,
  onClick: PropTypes.func.isRequired,
};

SubthemeListItem = withStyles(styles)(SubthemeListItem);

export default SubthemeListItem
