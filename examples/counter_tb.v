// Self-checking testbench for the 4-bit up counter.
// Prints "TEST PASSED" on success or "TEST FAILED" on any mismatch.
`timescale 1ns/1ps
module counter_tb;
    reg        clk = 0;
    reg        rst = 1;
    wire [3:0] count;

    integer    errors = 0;
    integer    i;

    counter dut (.clk(clk), .rst(rst), .count(count));

    // 10ns clock period.
    always #5 clk = ~clk;

    // Dump waveforms so you can open sim.vcd in GTKWave (refresher Week 2).
    initial begin
        $dumpfile("sim.vcd");
        $dumpvars(0, counter_tb);
    end

    initial begin
        // Hold reset for one rising edge, expect count == 0.
        @(posedge clk);
        #1;
        if (count !== 4'd0) begin
            errors = errors + 1;
            $display("FAIL: after reset count=%0d expected 0", count);
        end

        // Release reset and count up for 5 cycles.
        rst = 0;
        for (i = 1; i <= 5; i = i + 1) begin
            @(posedge clk);
            #1;
            if (count !== i[3:0]) begin
                errors = errors + 1;
                $display("FAIL: cycle %0d count=%0d expected %0d", i, count, i);
            end
        end

        if (errors == 0)
            $display("TEST PASSED");
        else
            $display("TEST FAILED (%0d errors)", errors);

        $finish;
    end
endmodule
