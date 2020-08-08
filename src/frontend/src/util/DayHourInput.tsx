import React from "react"
import {DayHour} from "./deleteSchedule";
import {Grid, InputBase, TextField, Typography, withStyles} from "@material-ui/core";
import {createStyles, makeStyles, Theme} from "@material-ui/core/styles";

interface DayHourInputProps {
    handler: ((dayHour: DayHour) => void);
}

const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        centerDiv: {
            textAlign: "left",
            margin: "10px auto",
            width: 180
        },
        inputFields: {
            borderBottom: '',
            width: '50%'
        },
        padding: {
            padding: '5px'
        },
        margin: {
            margin: 'auto'
        }
    }),
)

export const DayHourInputField: React.FC<DayHourInputProps> = (props: DayHourInputProps) => {
    const classes = useStyles();
    return (
        <div style={{margin: "10px"}}>
            <div className={classes.centerDiv}>
                <Grid spacing={4}>
                    <Grid container>
                        <TextField
                            className={classes.inputFields}
                            type={'number'}
                            variant={'outlined'}
                            InputProps={{
                                classes: {input: classes.padding},
                                inputProps: { min: 0}
                            }}
                        />
                        <Typography className={classes.margin}>Tage</Typography>
                    </Grid>
                    <br/>
                    <Grid container>
                        <TextField
                            className={classes.inputFields}
                            type={'number'}
                            variant={'outlined'}
                            InputProps={{
                                classes: {input: classes.padding},
                                inputProps: { min: 0, max: 23}
                            }}
                        />
                        <Typography className={classes.margin}>Stunden</Typography>
                    </Grid>
                </Grid>
            </div>
        </div>
    )
}