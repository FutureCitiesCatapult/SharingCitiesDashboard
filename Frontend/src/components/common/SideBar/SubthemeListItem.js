import React from 'react';
import PropTypes from 'prop-types';

import AttributeList from './AttributeList';

// material-ui
import { withStyles } from '@material-ui/core/styles';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import ExpandMore from '@material-ui/icons/ExpandMore';
import ChevronRight from '@material-ui/icons/ChevronRight';
import Collapse from '@material-ui/core/Collapse';
import Typography from '@material-ui/core/Typography';

const styles = (theme) => ({
  nested: {
    paddingLeft: theme.spacing.unit * 4,
  },
  listItemText: {
    // color: greyColor[800],
    color: theme.palette.primary.dark,
    fontWeight: 'bold'
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
              ? <ExpandMore color="secondary" />
              : <ChevronRight color="secondary"/>
          }
          <ListItemText
            disableTypography
            primary={<Typography variant="subtitle1" color="primary" className={classes.listItemText}>{subthemeName}</Typography>}
          />
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
