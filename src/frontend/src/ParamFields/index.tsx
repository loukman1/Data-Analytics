import React from 'react';
import { MenuItem, FormControlLabel, Checkbox, Collapse, TextField, Divider, FormLabel } from '@material-ui/core';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import ExpandLessIcon from '@material-ui/icons/ExpandLess';
import { useStyles } from '../JobCreate/style';
import { Param, ParamValues } from '../util/param';


interface ParamFieldProps extends ParamField {
    param: Param,
}

interface ParamFieldsProps extends ParamField {
    params: Param[],
}

interface ParamField {
    selectParamHandler: (_s: string, _a: any) => void,
    disabled: boolean,
    required: boolean,
    values: ParamValues
}

export const ParamFields: React.FC<ParamFieldsProps> = (props) => {
    const classes = useStyles();

    return (
        <div >
            {
                props.params.map(p => (
                    <div key={p.name}>
                        <div className={p.type === "boolean" ? classes.XSPaddingTB : classes.SPaddingTB}>
                            <ParamField
                                param={p}
                                values={props.values}
                                selectParamHandler={props.selectParamHandler}
                                disabled={props.disabled}
                                required={props.required}
                            />
                        </div>
                    </div>
                ))
            }
        </div>
    )
}

const ParamField: React.FC<ParamFieldProps> = (props) => {
    const param = props.param;
    const classes = useStyles();
    const [showSubParams, setShowSubParams] = React.useState(false);

    const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>, name: string) => {
        props.selectParamHandler(name, event.target.value);
    }
    const handleMultiChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>, name: string) => {
        const values = event.target.value.split(",");
        props.selectParamHandler(name, values);
    }
    const handleCheck = (event: React.ChangeEvent<HTMLInputElement>, name: string) => {
        props.selectParamHandler(name, event.target.checked);
    }

    const withExpIcon = (name: string, expanded: boolean) => {
        return (
            <span>
                {
                    expanded
                        ?
                        <div className={classes.expIcon}>
                            <ExpandLessIcon />
                        </div>
                        :
                        <div className={classes.expIcon}>
                            <ExpandMoreIcon />
                        </div>
                }
                {name} </span>
        )
    }


    switch (param.type) {
        case "string": case "number": case "multiString": case "multiNumber":
            const multiline = param.type === "multiString" || param.type === "multiNumber";
            return (
                <div>
                    <TextField
                        fullWidth
                        required={props.required && !param.optional}
                        multiline={multiline}
                        onChange={e => multiline ? handleMultiChange(e, param.name) : handleChange(e, param.name)}
                        variant="outlined"
                        value={props.values[param.name] || ""}
                        disabled={props.disabled}
                        label={param.displayName}
                    />
                </div>
            )
        case "boolean":
            return (
                <FormControlLabel
                    control={
                        < Checkbox
                            checked={props.values[param.name]}
                            onChange={e => handleCheck(e, param.name)}
                        />}
                    disabled={props.disabled}
                    label={
                        <FormLabel
                            disabled={props.disabled}>
                            {param.displayName}
                        </FormLabel>}
                    labelPlacement="start"
                    className={classes.checkboxParam}
                />
            )
        case "enum":
            return (
                <TextField
                    fullWidth
                    required={props.required && !param.optional}
                    onChange={e => handleChange(e, param.name)}
                    variant="outlined"
                    label={param.displayName}
                    value={props.values[param.name] || ""}
                    disabled={props.disabled}
                    select>
                    {param.enumValues.map((val) => (
                        <MenuItem key={val.value} value={val.value.toString()}>
                            {val.displayValue}
                        </MenuItem>
                    ))}
                </TextField>
            )
        case "subParams":
            return (
                <div>
                    <div className={classes.SPaddingTB}>
                        {param.optional
                            ?
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        checked={props.values[param.name]}
                                        onChange={e => handleCheck(e, param.name)}
                                    />}
                                label={
                                    <FormLabel
                                        disabled={props.disabled}>
                                        {withExpIcon(param.displayName, props.values[param.name])}
                                    </FormLabel>}
                                labelPlacement="start"
                                className={classes.checkboxParam}
                                disabled={props.disabled}
                            />
                            :
                            <div>
                                <FormLabel
                                    disabled={props.disabled}
                                    onClick={() => { setShowSubParams(!showSubParams) }}>
                                    {withExpIcon(param.displayName, showSubParams)}
                                </FormLabel>
                            </div>
                        }
                    </div>
                    <Collapse in={showSubParams || props.values[param.name]}>
                        <ParamFields
                            params={param.subParams}
                            values={props.values}
                            selectParamHandler={props.selectParamHandler}
                            disabled={props.disabled}
                            required={props.required}
                        />
                    </Collapse>
                    {((props.values[param.name] || showSubParams))
                        &&
                        <div className={classes.SPaddingTB}>
                            <Divider />
                        </div>}
                </div >
            )
        default:
            return (
                <div>
                    Unknown parameter type
                </div>
            )
    }
}
