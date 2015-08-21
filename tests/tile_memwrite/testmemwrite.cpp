/* Copyright (c) 2014 Quanta Research Cambridge, Inc
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */
#include "monkit.h"
#include "dmaManager.h"
#include "MemwriteIndication.h"
#include "MemwriteRequest.h"

#ifdef BOARD_xsim
static int numWords = 0x5000/4;
static int iterCnt = 1;
#elif defined(BSIM)
static int numWords = 0x124000/4;
static int iterCnt = 2;
#else
static int numWords = 0x1240000/4; // make sure to allocate at least one entry of each size
static int iterCnt = 128;
#endif
#ifdef PCIE
static int burstLen = 32;
#else
static int burstLen = 16;
#endif
#define TILE_NUMBER 1

static sem_t test_sem;
static size_t alloc_sz = numWords*sizeof(unsigned int);

class MemwriteIndication : public MemwriteIndicationWrapper
{
public:
    MemwriteIndication(int id, int tile=DEFAULT_TILE) : MemwriteIndicationWrapper(id,tile) {}
    void started(uint32_t words) {
        fprintf(stderr, "Memwrite::started: words=%x\n", words);
    }
    void writeDone ( uint32_t srcGen ) {
        fprintf(stderr, "Memwrite::writeDone (%08x)\n", srcGen);
        sem_post(&test_sem);
    }
    void reportStateDbg(uint32_t streamWrCnt, uint32_t srcGen) {
        fprintf(stderr, "Memwrite::reportStateDbg: streamWrCnt=%08x srcGen=%d\n", streamWrCnt, srcGen);
    }
};

int main(int argc, const char **argv)
{
    int mismatch = 0;
    uint32_t sg = 0;
    int max_error = 10;

    if (sem_init(&test_sem, 1, 0)) {
        fprintf(stderr, "error: failed to init test_sem\n");
        exit(1);
    }
    fprintf(stderr, "testmemwrite: start %s %s\n", __DATE__, __TIME__);
    DmaManager *dma = platformInit();
    MemwriteRequestProxy *device = new MemwriteRequestProxy(IfcNames_MemwriteRequestS2H,TILE_NUMBER);
    MemwriteIndication deviceIndication(IfcNames_MemwriteIndicationH2S,TILE_NUMBER);

    fprintf(stderr, "main::allocating memory...\n");
    int dstAlloc = portalAlloc(alloc_sz, 0);
    unsigned int *dstBuffer = (unsigned int *)portalMmap(dstAlloc, alloc_sz);
#ifdef FPGA0_CLOCK_FREQ
    long req_freq = FPGA0_CLOCK_FREQ, freq = 0;
    setClockFrequency(0, req_freq, &freq);
    fprintf(stderr, "Requested FCLK[0]=%ld actually %ld\n", req_freq, freq);
#endif
    unsigned int ref_dstAlloc = dma->reference(dstAlloc);
    for (int i = 0; i < numWords; i++)
        dstBuffer[i] = 0xDEADBEEF;
    portalCacheFlush(dstAlloc, dstBuffer, alloc_sz, 1);
    fprintf(stderr, "testmemwrite: flush and invalidate complete\n");
    fprintf(stderr, "testmemwrite: starting write %08x\n", numWords);
    portalTimerStart(0);
    device->startWrite(ref_dstAlloc, 0, numWords, burstLen, iterCnt);
    sem_wait(&test_sem);
    for (int i = 0; i < numWords; i++) {
        if (dstBuffer[i] != sg) {
            mismatch++;
            if (max_error-- > 0)
                fprintf(stderr, "testmemwrite: [%d] actual %08x expected %08x\n", i, dstBuffer[i], sg);
        }
        sg++;
    }
    platformStatistics();
    fprintf(stderr, "testmemwrite: mismatch count %d.\n", mismatch);
    exit(mismatch);
}