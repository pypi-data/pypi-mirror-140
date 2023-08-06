#include "log.h"
#include "solver.h"
#include <Python.h>
#include <structmember.h>

#define LARGE_VAL 1e30

typedef struct astrometry_extension_solver_t {
    PyObject_HEAD solver_t* solver;
} astrometry_extension_solver_t;

static void astrometry_extension_solver_dealloc(PyObject* self) {
    astrometry_extension_solver_t* current =
        (astrometry_extension_solver_t*)self;
    if (current->solver) {
        solver_free(current->solver);
        current->solver = NULL;
    }
    Py_TYPE(self)->tp_free(self);
}

static PyObject* astrometry_extension_solver_new(
    PyTypeObject* type,
    PyObject* args,
    PyObject* kwds) {
    return type->tp_alloc(type, 0);
}

static int astrometry_extension_solver_init(
    PyObject* self,
    PyObject* args,
    PyObject* kwds) {
    PyObject* paths;
    if (!PyArg_ParseTuple(args, "O", &paths)) {
        return -1;
    }
    if (!PyList_Check(paths)) {
        PyErr_SetString(PyExc_TypeError, "paths must be a list");
        return -1;
    }
    if (PyList_GET_SIZE(paths) == 0) {
        PyErr_SetString(PyExc_TypeError, "paths cannot be empty");
        return -1;
    }
    astrometry_extension_solver_t* current =
        (astrometry_extension_solver_t*)self;
    current->solver = solver_new();
    for (Py_ssize_t path_index = 0; path_index < PyList_GET_SIZE(paths);
         ++path_index) {
        PyObject* path = PyList_GET_ITEM(paths, path_index);
        if (!PyUnicode_Check(path)) {
            PyErr_SetString(
                PyExc_TypeError, "all the items in paths must be strings");
            break;
        }
        const char* filename = (const char*)PyUnicode_DATA(path);
        anqfits_t* fits = anqfits_open(filename);
        if (fits == NULL) {
            PyErr_Format(PyExc_TypeError, "loading \"%s\" failed", filename);
            break;
        }
        index_t* index = calloc(1, sizeof(index_t));
        index->fits = fits;
        index->indexfn = (char*)filename;
        if (index_reload(index) != 0) {
            anqfits_close(index->fits);
            free(index);
            PyErr_Format(PyExc_TypeError, "loading \"%s\" failed", filename);
            break;
        }
        index->indexfn = strdup(index->indexfn);
        index->indexname = strdup(quadfile_get_filename(index->quads));
        index->index_scale_upper =
            quadfile_get_index_scale_upper_arcsec(index->quads);
        index->index_scale_lower =
            quadfile_get_index_scale_lower_arcsec(index->quads);
        index->indexid = index->quads->indexid;
        index->healpix = index->quads->healpix;
        index->hpnside = index->quads->hpnside;
        index->dimquads = index->quads->dimquads;
        index->nquads = index->quads->numquads;
        index->nstars = index->quads->numstars;
        index->index_jitter = startree_get_jitter(index->starkd);
        if (index->index_jitter == 0.0) {
            index->index_jitter = DEFAULT_INDEX_JITTER;
        }
        index->cutnside = startree_get_cut_nside(index->starkd);
        index->cutnsweep = startree_get_cut_nsweeps(index->starkd);
        index->cutdedup = startree_get_cut_dedup(index->starkd);
        index->cutband = strdup_safe(startree_get_cut_band(index->starkd));
        index->cutmargin = startree_get_cut_margin(index->starkd);
        index_get_missing_cut_params(
            index->indexid,
            index->cutnside == -1 ? &index->cutnside : NULL,
            index->cutnsweep == 0 ? &index->cutnsweep : NULL,
            index->cutdedup == 0 ? &index->cutdedup : NULL,
            index->cutmargin == -1 ? &index->cutmargin : NULL,
            !index->cutband ? &index->cutband : NULL);
        index->circle =
            qfits_header_getboolean(index->codekd->header, "CIRCLE", 0);
        index->cx_less_than_dx =
            qfits_header_getboolean(index->codekd->header, "CXDX", FALSE);
        index->meanx_less_than_half =
            qfits_header_getboolean(index->codekd->header, "CXDXLT1", FALSE);
        solver_add_index(current->solver, index);
    }
    if (PyErr_Occurred()) {
        solver_free(current->solver);
        current->solver = NULL;
        return -1;
    }
    PyObject* logging = PyImport_ImportModule("logging");
    if (!logging) {
        solver_free(current->solver);
        current->solver = NULL;
        return -1;
    }
    PyObject* message = PyUnicode_FromFormat(
        "loaded %d index file%s",
        pl_size(current->solver->indexes),
        pl_size(current->solver->indexes) > 1 ? "s" : "");
    PyObject_CallMethod(logging, "info", "O", message);
    Py_DECREF(message);
    return 0;
}

typedef struct match_vector_t {
    MatchObj* data;
    size_t size;
    size_t capacity;
} match_vector_t;

static match_vector_t match_vector_with_capacity(size_t capacity) {
    if (capacity == 0) {
        match_vector_t match_vector = {
            NULL,
            0,
            0,
        };
        return match_vector;
    }
    match_vector_t match_vector = {
        malloc(sizeof(MatchObj) * capacity),
        0,
        capacity,
    };
    return match_vector;
}

static void match_vector_clear(match_vector_t* match_vector) {
    if (match_vector->capacity > 0) {
        free(match_vector->data);
        match_vector->data = NULL;
        match_vector->size = 0;
        match_vector->capacity = 0;
    }
}

static void
match_vector_reserve(match_vector_t* match_vector, size_t capacity) {
    if (capacity <= match_vector->capacity) {
        return;
    }
    match_vector->data =
        realloc(match_vector->data, sizeof(MatchObj) * capacity);
    match_vector->capacity = capacity;
}

static void match_vector_push(match_vector_t* match_vector, MatchObj* match) {
    if (match_vector->size == match_vector->capacity) {
        match_vector_reserve(
            match_vector,
            match_vector->capacity == 0 ? 1 : match_vector->capacity * 2);
    }
    memcpy(match_vector->data + match_vector->size, match, sizeof(MatchObj));
    match_vector->size += 1;
}

typedef struct callback_context_t {
    const char* solve_id;
    PyThreadState* save;
    PyObject* logging;
    solver_t* solver;
    double keep_logodds_threshold;
    match_vector_t matches;
} callback_context_t;

static anbool record_match_callback(MatchObj* match, void* userdata) {
    callback_context_t* context = (callback_context_t*)userdata;
    double ra = 0.0;
    double dec = 0.0;
    xyzarr2radecdeg(match->center, &ra, &dec);
    char logodds_string[24];
    snprintf(logodds_string, 24, "%g", match->logodds);
    char scale_string[24];
    snprintf(scale_string, 24, "%g", match->scale);
    char ra_string[24];
    snprintf(ra_string, 24, "%g", ra);
    char dec_string[24];
    snprintf(dec_string, 24, "%g", dec);
    PyEval_RestoreThread(context->save);
    PyObject* message = PyUnicode_FromFormat(
        "solve %s: logodds=%s, matches=%d, conflicts=%d, distractors=%d, "
        "index=%d, ra=%s, dec=%s, scale=%s",
        context->solve_id,
        logodds_string,
        match->nmatch,
        match->nconflict,
        match->ndistractor,
        match->nindex,
        ra_string,
        dec_string,
        scale_string);
    PyObject_CallMethod(context->logging, "info", "O", message);
    Py_DECREF(message);
    const int signal = PyErr_CheckSignals();
    context->save = PyEval_SaveThread();
    if (signal != 0) {
        context->solver->quit_now = TRUE;
    }
    if (match->logodds >= context->keep_logodds_threshold) {
        match_vector_push(&context->matches, match);
        match->theta = NULL;
        match->matchodds = NULL;
        match->refxyz = NULL;
        match->refxy = NULL;
        match->refstarid = NULL;
        match->testperm = NULL;
    }
    return FALSE;
}

static time_t timer_callback(void* userdata) {
    callback_context_t* context = (callback_context_t*)userdata;
    PyEval_RestoreThread(context->save);
    const int signal = PyErr_CheckSignals();
    context->save = PyEval_SaveThread();
    if (signal != 0) {
        context->solver->quit_now = TRUE;
        return 0;
    }
    return 1;
}

static PyObject*
astrometry_extension_solver_solve(PyObject* self, PyObject* args) {
    PyObject* stars_xs;
    PyObject* stars_ys;
    PyObject* stars_fluxes;
    PyObject* stars_backgrounds;
    double scale_lower = 0.0;
    double scale_upper = 0.0;
    PyObject* position_hint;
    const char* solve_id;
    double print_logodds_threshold = 0.0;
    double keep_logodds_threshold = 0.0;
    double tune_logodds_threshold = 0.0;
    if (!PyArg_ParseTuple(
            args,
            "OOOOddOsddd",
            &stars_xs,
            &stars_ys,
            &stars_fluxes,
            &stars_backgrounds,
            &scale_lower,
            &scale_upper,
            &position_hint,
            &solve_id,
            &print_logodds_threshold,
            &keep_logodds_threshold,
            &tune_logodds_threshold)) {
        return NULL;
    }
    astrometry_extension_solver_t* current =
        (astrometry_extension_solver_t*)self;
    if (scale_lower <= 0.0 || scale_upper <= 0.0 || scale_lower > scale_upper) {
        PyErr_SetString(
            PyExc_TypeError,
            "scale_lower and scale_upper must be strictly positive, and "
            "scale_lower must be smaller than scale_upper");
        return NULL;
    }
    const anbool has_position_hint = position_hint != Py_None;
    double position_hint_ra = 0.0;
    double position_hint_dec = 0.0;
    double position_hint_radius = 0.0;
    if (has_position_hint) {
        if (!PyTuple_Check(position_hint)) {
            PyErr_SetString(
                PyExc_TypeError, "position_hint must be None or a tuple");
            return NULL;
        }
        if (PyTuple_Size(position_hint) != 3) {
            PyErr_SetString(
                PyExc_TypeError, "position_hint must have 3 elements");
            return NULL;
        }
        position_hint_ra = PyFloat_AsDouble(PyTuple_GET_ITEM(position_hint, 0));
        if (PyErr_Occurred() || position_hint_ra < 0.0
            || position_hint_ra >= 360.0) {
            PyErr_Clear();
            PyErr_SetString(
                PyExc_TypeError,
                "position_hint.deg_ra must be a float in the range [0, 360[");
            return NULL;
        }
        position_hint_dec =
            PyFloat_AsDouble(PyTuple_GET_ITEM(position_hint, 1));
        if (PyErr_Occurred() || position_hint_dec < -90.0
            || position_hint_dec > 90.0) {
            PyErr_Clear();
            PyErr_SetString(
                PyExc_TypeError,
                "position_hint.deg_dec must be a float in the range [-90, 90]");
            return NULL;
        }
        position_hint_radius =
            PyFloat_AsDouble(PyTuple_GET_ITEM(position_hint, 2));
        if (PyErr_Occurred() || position_hint_radius < 0) {
            PyErr_Clear();
            PyErr_SetString(
                PyExc_TypeError,
                "position_hint.deg_radius must be a float larger than 0");
            return NULL;
        }
    }
    if (print_logodds_threshold > keep_logodds_threshold) {
        PyErr_SetString(
            PyExc_TypeError,
            "print_logodds_threshold cannot be larger than "
            "keep_logodds_threshold");
        return NULL;
    }
    if (!PyList_Check(stars_xs)) {
        PyErr_SetString(PyExc_TypeError, "stars_xs must be a list");
        return NULL;
    }
    if (!PyList_Check(stars_ys)) {
        PyErr_SetString(PyExc_TypeError, "stars_ys must be a list");
        return NULL;
    }
    const anbool has_fluxes = stars_fluxes != Py_None;
    if (has_fluxes && !PyList_Check(stars_fluxes)) {
        PyErr_SetString(PyExc_TypeError, "stars_fluxes must be None or a list");
        return NULL;
    }
    const anbool has_backgrounds = stars_backgrounds != Py_None;
    if (has_backgrounds && !PyList_Check(stars_backgrounds)) {
        PyErr_SetString(
            PyExc_TypeError, "stars_backgrounds must be None or a list");
        return NULL;
    }
    const Py_ssize_t stars_size = PyList_GET_SIZE(stars_xs);
    if (stars_size != PyList_GET_SIZE(stars_ys)) {
        PyErr_SetString(
            PyExc_TypeError, "stars_xs and stars_ys must have the same size");
        return NULL;
    }
    if (stars_size == 0) {
        PyErr_SetString(PyExc_TypeError, "stars_xs cannot be empty");
        return NULL;
    }
    if (has_fluxes && stars_size != PyList_GET_SIZE(stars_fluxes)) {
        PyErr_SetString(
            PyExc_TypeError,
            "stars_xs and stars_fluxes must have the same size");
        return NULL;
    }
    if (has_backgrounds && stars_size != PyList_GET_SIZE(stars_backgrounds)) {
        PyErr_SetString(
            PyExc_TypeError,
            "stars_xs and stars_backgrounds must have the same size");
        return NULL;
    }
    PyObject* logging = PyImport_ImportModule("logging");
    if (!logging) {
        return NULL;
    }
    {
        PyObject* message = PyUnicode_FromFormat("solve %s: start", solve_id);
        PyObject_CallMethod(logging, "info", "O", message);
        Py_DECREF(message);
    }
    starxy_t starxy;
    starxy.xlo = LARGE_VAL;
    starxy.xhi = -LARGE_VAL;
    starxy.ylo = LARGE_VAL;
    starxy.yhi = -LARGE_VAL;
    starxy.N = (int)stars_size;
    starxy.x = malloc(sizeof(double) * starxy.N);
    starxy.y = malloc(sizeof(double) * starxy.N);
    starxy.flux = has_fluxes ? malloc(sizeof(double) * starxy.N) : NULL;
    starxy.background =
        has_backgrounds ? malloc(sizeof(double) * starxy.N) : NULL;
    for (Py_ssize_t index = 0; index < stars_size; ++index) {
        starxy.x[index] = PyFloat_AsDouble(PyList_GET_ITEM(stars_xs, index));
        starxy.y[index] = PyFloat_AsDouble(PyList_GET_ITEM(stars_ys, index));
        if (starxy.x[index] < starxy.xlo) {
            starxy.xlo = starxy.x[index];
        }
        if (starxy.x[index] > starxy.xhi) {
            starxy.xhi = starxy.x[index];
        }
        if (starxy.y[index] < starxy.ylo) {
            starxy.ylo = starxy.y[index];
        }
        if (starxy.y[index] > starxy.yhi) {
            starxy.yhi = starxy.y[index];
        }
        if (has_fluxes) {
            starxy.flux[index] =
                PyFloat_AsDouble(PyList_GET_ITEM(stars_fluxes, index));
        }
        if (has_backgrounds) {
            starxy.background[index] =
                PyFloat_AsDouble(PyList_GET_ITEM(stars_backgrounds, index));
        }
    }
    if (PyErr_Occurred()) {
        starxy_free_data(&starxy);
        PyErr_Clear();
        PyErr_SetString(
            PyExc_TypeError,
            "items in stars_xs, stars_ys, stars_fluxes, and stars_backgrounds "
            "must be floats");
        return NULL;
    }
    callback_context_t context = {
        solve_id,
        PyEval_SaveThread(),
        logging,
        NULL,
        keep_logodds_threshold,
        match_vector_with_capacity(8),
    };
    context.solver = solver_new();
    context.solver->indexes = current->solver->indexes;
    context.solver->fieldxy = NULL;
    context.solver->pixel_xscale = 0.0;
    context.solver->predistort = NULL;
    context.solver->fieldxy_orig = &starxy;
    context.solver->funits_lower = scale_lower;
    context.solver->funits_upper = scale_upper;
    context.solver->logratio_toprint = print_logodds_threshold;
    context.solver->logratio_tokeep = keep_logodds_threshold;
    context.solver->logratio_totune = tune_logodds_threshold;
    context.solver->record_match_callback = record_match_callback;
    context.solver->userdata = &context;
    context.solver->do_tweak = TRUE;
    context.solver->timer_callback = timer_callback;
    if (has_position_hint) {
        solver_set_radec(
            context.solver,
            position_hint_ra,
            position_hint_dec,
            position_hint_radius);
    }
    context.solver->have_best_match =
        TRUE; // prevent best match copy (done in the callback)
    solver_run(context.solver);
    context.solver->have_best_match = FALSE;
    PyEval_RestoreThread(context.save);
    if (PyErr_Occurred()) {
        context.solver->indexes = NULL;
        context.solver->fieldxy_orig = NULL;
        starxy_free_data(&starxy);
        solver_free(context.solver);
        return NULL;
    }
    PyObject* result = NULL;
    if (context.matches.size > 0) {
        for (size_t index = 0; index < context.matches.size; ++index) {
            MatchObj* match = context.matches.data + index;
            printf(
                "match loggods=%g, sip=%p, dimquads=%d\n",
                match->logodds,
                match->sip,
                +match->dimquads); // @DEV
        }

        // result = (
        //     stars=((x, y, ra, dec), ...),
        //     (
        //         (
        //             logodds,
        //             (center_ra, center_dec),
        //             scale,
        //             stars_indices=(index, ...),
        //             quad_stars_indices=(index, ...),
        //         ),
        //         ...
        //     ),
        // )
        /*
        result = PyTuple_New(3);
        {
            double ra = 0.0;
            double dec = 0.0;
            xyzarr2radecdeg(context.solver->best_match.center, &ra, &dec);
            PyObject* center = PyTuple_New(2);
            PyTuple_SET_ITEM(center, 0, PyFloat_FromDouble(ra));
            PyTuple_SET_ITEM(center, 1, PyFloat_FromDouble(dec));
            PyTuple_SET_ITEM(result, 0, center);
        }
        PyTuple_SET_ITEM(
            result, 1, PyFloat_FromDouble(context.solver->best_match.scale));
        PyTuple_SET_ITEM(
            result, 2, PyFloat_FromDouble(context.solver->best_logodds));
        */
    } else {
        Py_INCREF(Py_None);
        result = Py_None;
    }
    match_vector_clear(&context.matches);
    context.solver->indexes = NULL;
    context.solver->fieldxy_orig = NULL;
    starxy_free_data(&starxy);
    solver_free(context.solver);
    return result;
}

static PyMemberDef astrometry_extension_solver_members[] = {
    {NULL, 0, 0, 0, NULL},
};

static PyTypeObject astrometry_extension_solver_type = {
    PyVarObject_HEAD_INIT(NULL, 0)};

static PyMethodDef astrometry_extension_solver_methods[] = {
    {"solve", astrometry_extension_solver_solve, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static PyMethodDef astrometry_extension_methods[] = {{NULL, NULL, 0, NULL}};

static struct PyModuleDef astrometry_extension_definition = {
    PyModuleDef_HEAD_INIT,
    "astrometry_extension",
    "Astrometry.net core functions wrapper",
    -1,
    astrometry_extension_methods};

PyMODINIT_FUNC PyInit_astrometry_extension() {
    PyObject* module = PyModule_Create(&astrometry_extension_definition);
    astrometry_extension_solver_type.tp_name = "astrometry_extension.Solver";
    astrometry_extension_solver_type.tp_basicsize =
        sizeof(astrometry_extension_solver_t);
    astrometry_extension_solver_type.tp_dealloc =
        astrometry_extension_solver_dealloc;
    astrometry_extension_solver_type.tp_flags =
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;
    astrometry_extension_solver_type.tp_methods =
        astrometry_extension_solver_methods;
    astrometry_extension_solver_type.tp_members =
        astrometry_extension_solver_members;
    astrometry_extension_solver_type.tp_new = astrometry_extension_solver_new;
    astrometry_extension_solver_type.tp_init = astrometry_extension_solver_init;
    PyType_Ready(&astrometry_extension_solver_type);
    PyModule_AddObject(
        module, "Solver", (PyObject*)&astrometry_extension_solver_type);
    return module;
}
