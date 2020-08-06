import React, { useEffect } from "react";
import { ParamValues, toTypedValues, trimParamValues, validateParamValues, initSelectedValues } from "../util/param";
import { Button, Container, Fade, InputBase, Modal, Paper, withStyles, TextField } from "@material-ui/core";
import Accordion from "@material-ui/core/Accordion";
import { AccordionSummary, useStyles } from "./style";
import ExpandLess from "@material-ui/icons/ExpandLess";
import ExpandMore from "@material-ui/icons/ExpandMore";
import Typography from "@material-ui/core/Typography";
import IconButton from "@material-ui/core/IconButton";
import EditIcon from "@material-ui/icons/Edit";
import DeleteIcon from '@material-ui/icons/Delete';
import CheckCircleIcon from "@material-ui/icons/CheckCircle";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import Grid from "@material-ui/core/Grid";
import Backdrop from "@material-ui/core/Backdrop";
import { ContinueButton } from "../JobCreate/ContinueButton";
import { Job } from "./index";
import { ScheduleSelection } from "../JobCreate/ScheduleSelection";
import { useCallFetch } from "../Hooks/useCallFetch";
import { ParamFields } from "../ParamFields";
import {
    Schedule,
    withFormattedDates,
    showSchedule,
    fromFormattedDates,
    showTimeToNextDate,
    validateSchedule
} from "../util/schedule";
import { getUrl } from "../util/fetchUtils";
import { Notification, TMessageStates } from "../util/Notification";


interface Props {
    job: Job,
    getJobs: () => void;
}

interface INotification {
    open: boolean,
    stateType: TMessageStates,
    message: string
}

export const JobItem: React.FC<Props> = ({ job, getJobs }) => {
    const classes = useStyles();

    const [state, setState] = React.useState({
        edit: true,
        editIcon: 'block',
        doneIcon: 'none'
    });

    const NameInput = withStyles({
        root: {
            cursor: "pointer",
        },
        input: {
            cursor: state.edit ? 'pointer' : 'text',
            padding: '0 8px',
            marginLeft: '8px',
            color: 'white',
            fontSize: '1.5625rem',
            borderBottom: state.edit ? '' : '2px solid #c4c4c4'
        },
    })(InputBase);

    const [expanded, setExpanded] = React.useState<string | false>(false);
    const [jobName, setJobName] = React.useState(job.jobName);
    const [open, setOpen] = React.useState(false);
    const [paramValues, setParamValues] = React.useState<ParamValues>({ ...initSelectedValues(job.params), ...job.values });
    const [schedule, setSchedule] = React.useState<Schedule>(fromFormattedDates(job.schedule));
    const [next, setNext] = React.useState(showTimeToNextDate(schedule));
    const [error, setError] = React.useState(false);
    const [errorMessage, setErrorMessage] = React.useState("");
    const [success, setSucess] = React.useState<INotification>({
        open: false,
        stateType: "success",
        message: ""
    });

    const handleSelectSchedule = (schedule: Schedule) => {
        setSchedule(schedule);
    }

    const handleSelectParam = (key: string, value: any) => {
        const updated = { ...paramValues }
        updated[key] = value;
        setParamValues(updated);
    }

    const handleJobName = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setJobName(event.target.value);
    }

    const handleEditError = () => {
        setSucess({ open: true, stateType: "error", message: "Bearbeitung fehlgeschlagen" })
    }

    const handleEditSuccess = () => {
        getJobs()
        setSucess({ open: true, stateType: "success", message: "Job erfolgreich geändert" })
    }

    const deleteJob = useCallFetch(getUrl(`/remove/${job.jobId}`), { method: 'DELETE' }, getJobs);

    const editJob = useCallFetch(getUrl(`/edit/${job.jobId}`), {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            jobName: jobName.trim(),
            values: toTypedValues(trimParamValues(paramValues), job.params),
            schedule: withFormattedDates(schedule)
        })
    }, handleEditSuccess, handleEditError);

    useEffect(() => {
        const interval = setInterval(() => {
            setNext(showTimeToNextDate(schedule));
        }, 60000);
        return () => clearInterval(interval);
    }, [schedule]);

    useEffect(() => {
        setNext(showTimeToNextDate(schedule));
    }, [schedule]);

    const renderJobItem = (job: Job) => {
        const handleOpen = () => {
            setOpen(true);
        };
        const handleClose = () => {
            setOpen(false);
        };
        const handleChange = (panel: string) => (event: React.ChangeEvent<{}>, isExpanded: boolean) => {
            setExpanded(isExpanded ? panel : false);
        };
        const handleEditClick = () => {
            setState(state.edit ? { edit: false, editIcon: 'none', doneIcon: 'block' } : {
                edit: true,
                editIcon: 'block',
                doneIcon: 'none'
            });
            setExpanded(String(job.jobId));
        }

        const handleCheckClick = () => {
            if (jobName.trim() === "") {
                setErrorMessage("Jobname nicht ausgefüllt");
                setError(true);
                return;
            }
            if (!validateParamValues(paramValues, job.params)) {
                setErrorMessage("Pflichtparameter nicht gesetzt");
                setError(true);
                return;
            }
            if (!validateSchedule(schedule)) {
                setErrorMessage("Es muss mindestens ein Wochentag ausgewählt werden");
                setError(true);
                return;
            }
            handleEditClick();
            editJob();
        }
        const handleSaveModal = () => {
            handleCheckClick();
            handleClose();
        }

        const renderTextField = () => {
            return (
                <div>
                    <div className={classes.SPaddingTRB}>
                        <TextField
                            label="Thema"
                            defaultValue={job.topicName}
                            InputProps={{
                                disabled: true,
                            }}
                            variant="outlined"
                            fullWidth
                        />
                    </div>
                    <div className={classes.SPaddingTRB}>
                        <Button className={classes.inputButton} onClick={handleOpen}>
                            <TextField
                                label="Zeitplan"
                                value={showSchedule(schedule)}
                                InputProps={{
                                    disabled: state.edit,
                                    readOnly: true
                                }}
                                required={!state.edit}
                                variant="outlined"
                                fullWidth
                            />
                        </Button>

                    </div>
                    <div className={classes.SPaddingTRB}>
                        <TextField
                            label="nächstes Video"
                            value={next}
                            InputProps={{
                                disabled: true,
                            }}
                            variant="outlined"
                            fullWidth
                        />
                    </div>
                </div>
            )
        }

        const handleCloseError = () => {
            setError(false);
        }
        const handleCloseSuccess = () => {
            setSucess({ open: false, stateType: success.stateType, message: success.message });
        }

        return (
            <div className={classes.root}>
                <Accordion expanded={expanded === String(job.jobId)} onChange={handleChange(String(job.jobId))}>
                    <AccordionSummary>
                        {expanded ? <ExpandLess className={classes.expIcon} /> :
                            <ExpandMore className={classes.expIcon} />}
                        <Typography component="span" className={classes.heading}>#{job.jobId}
                            <NameInput
                                // autoFocus={true}
                                value={jobName}
                                readOnly={state.edit}
                                onClick={state.edit ? () => {
                                } : (event) => event.stopPropagation()}
                                onChange={handleJobName}
                            >
                                {job.jobName}</NameInput></Typography>
                        <Notification handleClose={handleCloseError} open={error} message={errorMessage}
                            type={"error"} />
                        <Notification handleClose={handleCloseSuccess} open={success.open} message={success.message}
                            type={success.stateType} />
                        <div onClick={(event) => event.stopPropagation()}>
                            <IconButton style={{ display: state.editIcon }} className={classes.button}
                                onClick={handleEditClick}>
                                <EditIcon />
                            </IconButton>
                            <IconButton style={{ display: state.doneIcon }} className={classes.button}
                                onClick={handleCheckClick}>
                                <CheckCircleIcon />
                            </IconButton>
                        </div>
                        <div onClick={(event) => event.stopPropagation()}>
                            <IconButton onClick={deleteJob} className={classes.button}>
                                <DeleteIcon />
                            </IconButton>
                        </div>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Grid item md={6}>
                            {renderTextField()}
                        </Grid>
                        <Modal
                            aria-labelledby="transition-modal-title"
                            aria-describedby="transition-modal-description"
                            className={classes.modal}
                            open={open}
                            onClose={handleClose}
                            closeAfterTransition
                            BackdropComponent={Backdrop}
                            BackdropProps={{
                                timeout: 500,
                            }}
                        >
                            <Fade in={open}>
                                <Container className={classes.backdropContent}>
                                    <Paper variant="outlined" className={classes.paper}>
                                        <ScheduleSelection
                                            schedule={schedule}
                                            selectScheduleHandler={handleSelectSchedule}
                                        />
                                        <ContinueButton onClick={handleSaveModal}>SPEICHERN</ContinueButton>
                                    </Paper>
                                </Container>
                            </Fade>
                        </Modal>
                        <Grid item md={6}>
                            <div>
                                <ParamFields
                                    params={job.params}
                                    values={paramValues}
                                    selectParamHandler={handleSelectParam}
                                    disabled={state.edit}
                                    required={!state.edit}
                                />
                            </div>
                        </Grid>
                    </AccordionDetails>
                </Accordion>
            </div>
        );
    }

    return (
        renderJobItem(job)
    )
}