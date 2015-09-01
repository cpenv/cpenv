#!/bin/bash
export PS1


function cpenv() {

    pyout="tmp_pyout"
    pycpenv "$@" > $pyout

    if is_bash_script $pyout; then
        source $pyout
    else
        cat $pyout
    fi

    rm -f $pyout

}


function run_py() {

    pyout="tmp_pyout"
    python "$@" > $pyout

    if is_bash_script $pyout; then
        source $pyout
    else
        cat $pyout
    fi

    rm -f $pyout

}


function is_bash_script() {
    pyout=$1
    header=$(head -n 1 $pyout)
    if [[ $header == \#\!/bin/bash* ]]; then
        return 0
    else
        return 1
    fi
}
